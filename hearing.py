"""Module for scraping hearing information"""
from decimal import Decimal
import os
import re
import sys
import itertools
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import logging
from statuses import statuses_map
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from emailing import log_and_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout)


def get_test_html_path(index: int, page_type: str) -> str:
    this_directory = os.path.dirname(os.path.realpath(__file__))
    test_filepath = os.path.join(this_directory, page_type, f"example_{index}.html")
    return test_filepath


def get_test_filing_search_path() -> str:
    """Used for testing the separate module "parse_filings.py"."""
    this_directory = os.path.dirname(os.path.realpath(__file__))
    test_filepath = os.path.join(
        this_directory, "test_search_pages", f"example_case_query_result.html"
    )
    return test_filepath


def load_soup_from_filepath(filepath: str) -> BeautifulSoup:
    with open(filepath) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    return soup


def get_test_soup(index: int) -> BeautifulSoup:
    filepath = get_test_html_path(index, page_type="test_pages")
    return load_soup_from_filepath(filepath)


def get_test_search_page(index: int) -> BeautifulSoup:
    filepath = get_test_html_path(index, page_type="test_search_pages")
    return load_soup_from_filepath(filepath)


def get_test_filings_search_page() -> BeautifulSoup:
    """
    Used for testing the separate module "parse_filings.py".

    This may or may not need to be distinct from get_test_search_page above.
    Possibly the functions being tested can be consolidated.
    """
    filepath = get_test_filing_search_path()
    return load_soup_from_filepath(filepath)


def get_plaintiff(soup):
    # TODO handle multiple plaintiffs
    tag = get_plaintiff_elements(soup)[0]
    name_elem = tag.find_next_sibling("th")

    return name_elem.text


def get_plaintiff_elements(soup):
    """
    Gets the plaintiff HTML elements from a CaseDetail.
    These are currently used as an anchor for most of the Party Info parsing.
    """
    return soup.find_all("th", text="Plaintiff")


def get_defendant_elements(soup):
    """
    Gets the defendant HTML elements from a CaseDetail.
    These are currently used as an anchor for most of the Party Info parsing.
    Sometimes the text of the element does not always say "Defendant", but may say something like "Defendant 2".
    """
    return soup.find_all("th", text=re.compile(r"^Defendant"))


def get_defendants(soup):
    defendants = []
    for tag in get_defendant_elements(soup):
        name_elem = tag.find_next_sibling("th")
        defendants.append(name_elem.text)
    together = "; ".join(defendants)
    return together


def get_attorneys_header_id(soup: BeautifulSoup) -> Optional[str]:
    """Get the HTML ID attribute for the "Attorneys" column header."""
    element = soup.find("th", text="Attorneys")
    if not element:
        return None

    return element.get("id")


def get_attorneys_for_party(
    soup: BeautifulSoup, party_elements
) -> Dict[str, List[str]]:
    """Get the attorney(s) for a party."""
    attorneys: Dict[str, List[str]] = dict()
    attorneys_header_id = get_attorneys_header_id(soup)

    for party_element in party_elements:
        try:
            party_name = party_element.find_next_sibling("th").text.strip()

            party_element_id = party_element.get("id")
            party_attorney_element = soup.find(
                "td",
                headers=lambda _headers: _headers
                and attorneys_header_id in _headers
                and party_element_id in _headers,
            )
            party_attorney_name = party_attorney_element.find("b").text.strip()
        except AttributeError:
            continue

        if party_attorney_name not in attorneys:
            attorneys[party_attorney_name] = []

        attorneys[party_attorney_name].append(party_name)

    return attorneys


def get_attorneys_for_defendants(soup: BeautifulSoup) -> Dict[str, List[str]]:
    """Get the attorney(s) for the defendant(s)."""
    defendant_elements = get_defendant_elements(soup)
    return get_attorneys_for_party(soup, defendant_elements)


def get_attorneys_for_plaintiffs(soup: BeautifulSoup) -> Dict[str, List[str]]:
    """Get the attorney(s) for the plaintiff(s)."""
    plaintiff_elements = get_plaintiff_elements(soup)
    return get_attorneys_for_party(soup, plaintiff_elements)


def get_case_number(soup):
    elem = soup.find(class_="ssCaseDetailCaseNbr").span
    return elem.text


def get_style(soup):
    elem = soup.find_all("table")[4].tbody.tr.td
    return elem.text


def get_date_filed(soup: BeautifulSoup) -> str:
    """Get date filed for the case filing. """
    elem = soup.find_all("table")[4].find("th", text="Date Filed:").find_next("b")
    return elem.text


def get_zip(party_info_th_soup) -> str:
    """Returns a ZIP code from the Table Heading Party Info of a CaseDetail"""
    zip_regex = re.compile(r", tx \d{5}(-\d{4})?")

    def has_zip(string: str) -> bool:
        return bool(zip_regex.search(string.lower()))

    zip_tag = party_info_th_soup.find_next(string=has_zip)
    return zip_tag.strip().split()[-1] if zip_tag is not None else ""


def get_disposition_tr_element(soup) -> str:
    """
    Returns the <tr> element of a CaseDetail document that contains Disposition info, if one exists.
    """
    disp_date_th = soup.find(
        "th", id=lambda id_str: id_str is not None and "RDISPDATE" in id_str
    )
    return disp_date_th.parent if disp_date_th is not None else None


def get_disposition_type(disposition_tr) -> str:
    return disposition_tr.find("b").text


def get_disposition_awarded_to(disposition_tr) -> str:
    """
    Gets the "Awarded To" field of a disposition, if one exists.
    """
    if disposition_tr is None:
        return None

    award_field = disposition_tr.find(text=re.compile(r"Awarded To:"))

    if award_field is None:
        return None

    return award_field.next_sibling.text.strip()


def get_disposition_awarded_against(disposition_tr) -> str:
    """
    Gets the "Awarded Against" field of a disposition, if one exists.
    """
    if disposition_tr is None:
        return None

    award_field = disposition_tr.find(text=re.compile(r"Awarded Against:"))

    if award_field is None:
        return None

    return award_field.next_sibling.text.strip()


def get_events_tbody_element(soup):
    """
    Returns the <tbody> element  of a CaseDetail document that contains Dispositions, Hearings, and Other Events.
    Used as a starting point for many event parsing methods.
    """
    table_caption_div = soup.find(
        "div", class_="ssCaseDetailSectionTitle", text="Events & Orders of the Court"
    )
    tbody = table_caption_div.parent.find_next_sibling("tbody")
    return tbody


def get_hearing_tags(soup) -> List:
    """
    Returns <tr> elements in the Events and Hearings section of a CaseDetail document that represent a hearing record.
    """
    root = get_events_tbody_element(soup)
    hearing_ths = root.find_all(
        "th", id=lambda id_str: id_str is not None and id_str.startswith("RCDHR")
    )
    hearing_trs = [hearing_th.parent for hearing_th in hearing_ths]

    return hearing_trs or []


def get_hearing_and_event_tags(soup) -> List:
    """
    Returns <tr> elements in the Events and Hearings section of a CaseDetail document.
    """
    root = get_events_tbody_element(soup)
    hearing_or_event_ths = root.find_all(
        "th", id=lambda id_str: id_str is not None and id_str.startswith("RCD")
    )
    hearing_or_event_trs = [hearing_th.parent for hearing_th in hearing_or_event_ths]

    return hearing_or_event_trs or []


def get_hearing_text(hearing_tag) -> str:
    return hearing_tag.find("b").next_sibling if hearing_tag is not None else ""


def get_hearing_date(hearing_tag) -> str:
    if hearing_tag is None:
        return ""
    date_tag = hearing_tag.find("th")
    return date_tag.text


def get_hearing_type(hearing_tag) -> str:
    """Function to get all events and case type from case page section: Other Events and Hearings"""
    hearing_type = hearing_tag.find_all("b")[0].text
    all_tds = hearing_tag.find_all("td")
    all_text = all_tds[-1].get_text(separator=" ")

    if not all_text:
        for td in all_tds:
            text = td.get_text(separator=" ")
            if len(text) > 1 and text not in all_text:
                all_text += text

    return hearing_type, all_text


def get_hearing_time(hearing_tag) -> str:
    hearing_text = get_hearing_text(hearing_tag)
    hearing_time_matches = re.search(r"\d{1,2}:\d{2} [AP]M", hearing_text)
    return hearing_time_matches[0] if hearing_time_matches is not None else ""


def get_hearing_officer(hearing_tag) -> str:
    hearing_text = get_hearing_text(hearing_tag)
    officer_groups = hearing_text.split("Judicial Officer")
    name = officer_groups[1] if len(officer_groups) > 1 else ""
    return name.strip().strip(")")


def get_disposition_date_node(soup) -> BeautifulSoup:
    try:
        return soup.find("th", id="RDISPDATE1")
    except:
        return None


def get_disposition_date(soup) -> Optional[str]:
    disposition_date_node = get_disposition_date_node(soup)
    return disposition_date_node.text if disposition_date_node else None


def get_disposition_amount(soup) -> Optional[Decimal]:
    disposition_date_node = get_disposition_date_node(soup)
    if disposition_date_node is None:
        return None
    disposition_label = disposition_date_node.find_next_sibling(
        "td", headers="CDisp RDISPDATE1"
    )
    disposition_amount_node = disposition_label.find("nobr")
    if disposition_amount_node is None:
        return None
    if "$" not in disposition_amount_node.text:
        return None
    amount_as_string = disposition_amount_node.text.strip(". ")
    amount = Decimal(re.sub(r"[^\d.]", "", amount_as_string))
    return amount


def get_precinct_number(soup) -> int:
    word_to_number = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    location_heading = soup.find(text="Location:").parent
    precinct_name = location_heading.find_next_sibling("td").text
    precinct_number = precinct_name.split("Precinct ")[1]

    return word_to_number[precinct_number]


def get_status_and_type(status_soup) -> str:
    tds = status_soup.find_all("td")
    divs = tds[-1].find_all("div")
    status, type = divs[1].text, divs[0].text
    return status, type


def get_register_url(status_soup) -> str:
    link_tag = status_soup.find(style="color: blue")
    relative_link = link_tag.get("href")
    return "https://odysseypa.traviscountytx.gov/JPPublicAccess/" + relative_link


def get_comments(soup: BeautifulSoup) -> Optional[str]:
    """Get comments from case page."""

    disposition_date_node = get_disposition_date_node(soup)
    if not disposition_date_node:
        return None  # comments

    disposition_label = disposition_date_node.find_next_sibling(
        "td", headers="CDisp RDISPDATE1"
    )
    if not disposition_label:
        return None  # comments

    comments = [
        nobr.text
        for nobr in disposition_label.find_all("nobr")
        if nobr.text.startswith("Comment:")
    ]
    if len(comments) >= 1:
        return comments[0]
    else:
        return None


def get_case_event_date_basic(soup: BeautifulSoup, event_name: str) -> Optional[str]:
    """Get date for case event entries that only include event name."""
    case_event_date: Optional[str] = None

    case_events = get_events_tbody_element(soup)
    event_label = case_events.find("b", text=event_name)
    if event_label:
        try:
            case_event_tr = event_label.parent.parent
            case_event_date = case_event_tr.find("th", class_="ssTableHeaderLabel").text
        except AttributeError:
            pass

    return case_event_date


def get_writ(soup: BeautifulSoup) -> Dict[str, str]:
    """Get details for the "Writ" case event."""
    event_details: Dict[str, str] = {}

    case_events = get_events_tbody_element(soup)
    event_label = case_events.find("b", text="Writ")
    if not event_label:
        return event_details

    event_tr = event_label.parent.parent.parent.parent.parent.parent

    try:
        event_details["case_event_date"] = event_tr.find(
            "th", class_="ssTableHeaderLabel"
        ).text
    except AttributeError:
        pass

    served_td = event_tr.find("td", text="Served")
    if served_td:
        try:
            event_details["served_date"] = served_td.find_next_sibling("td").text
        except AttributeError:
            pass

        try:
            event_details[
                "served_subject"
            ] = served_td.parent.parent.parent.parent.find_previous_sibling("td").text
        except AttributeError:
            pass

    returned_td = event_tr.find("td", text="Returned")
    if returned_td:
        try:
            event_details["returned_date"] = returned_td.find_next_sibling("td").text
        except AttributeError:
            pass

    return event_details


def get_writ_of_possession_service(soup: BeautifulSoup) -> Dict[str, str]:
    """Get details for the "Writ of Possession Service" case event."""
    event_details: Dict[str, str] = {}

    event_date = get_case_event_date_basic(soup, "Writ of Possession Service")
    if event_date:
        event_details["case_event_date"] = event_date

    return event_details


def get_writ_of_possession_requested(soup: BeautifulSoup) -> Dict[str, str]:
    """Get details for the "Writ of Possession Requested" case event."""
    event_details: Dict[str, str] = {}

    event_date = get_case_event_date_basic(soup, "Writ of Possession Requested")
    if event_date:
        event_details["case_event_date"] = event_date

    return event_details


def get_writ_of_possession_sent_to_constable(soup: BeautifulSoup) -> Dict[str, str]:
    """Get details for the "Writ of Possession Sent to Constable's Office" case event."""
    event_details: Dict[str, str] = {}

    event_date = get_case_event_date_basic(
        soup, "Writ of Possession Sent to Constable's Office"
    )
    if event_date:
        event_details["case_event_date"] = event_date

    return event_details


def get_writ_returned_to_court(soup: BeautifulSoup) -> Dict[str, str]:
    """Get details for the "Writ Returned to Court" case event."""
    event_details: Dict[str, str] = {}

    event_date = get_case_event_date_basic(soup, "Writ Returned to Court")
    if event_date:
        event_details["case_event_date"] = event_date

    return event_details


def did_defendant_appear(hearing_tag) -> bool:
    """If and only if "appeared" appears, infer defendant apparently appeared."""

    if hearing_tag is None:
        return False

    def appeared_in_text(text):
        return text and re.compile("[aA]ppeared").search(text)

    appeared_tag = hearing_tag.find(text=appeared_in_text)
    return appeared_tag is not None


def was_defendant_served(soup) -> List[str]:
    dates_of_service = {}
    served_tags = soup.find_all(text="Served")
    for service_tag in served_tags:
        date_tag = service_tag.parent.find_next_sibling("td")
        defendant_tag = service_tag.parent.parent.parent.parent.parent.find_previous_sibling(
            "td"
        )
        dates_of_service[defendant_tag.text] = date_tag.text

    return dates_of_service


def was_defendant_alternative_served(soup) -> List[str]:
    dates_of_service = []
    served_tags = soup.find_all(text="Order Granting Alternative Service")
    for service_tag in served_tags:
        date_tag = service_tag.parent.parent.find_previous_sibling("th")
        dates_of_service.append(date_tag.text)

    return dates_of_service


def make_parsed_hearing(soup):

    try:
        time = _time(soup)
    except:
        time = None

    try:
        officer = get_hearing_officer(soup)
    except:
        officer = None

    try:
        appeared = did_defendant_appear(soup)
    except:
        appeared = None

    type, all_text = get_hearing_type(soup)

    return {
        "hearing_date": get_hearing_date(soup),
        "hearing_time": time,
        "hearing_officer": officer,
        "appeared": appeared,
        "hearing_type": type,
        "all_text": all_text,
    }


THRESH = 75


def lt(i):
    if i > THRESH:
        return i
    else:
        return 0


def fuzzy(i):
    j = fuzz.partial_ratio(i[0].upper(), i[1].upper())
    return j


def match_wordwise(awarded_to, plaintiff, defendant):
    # Split into word lists
    a_l = [x.strip(",") for x in awarded_to.split()]
    p_l = [x.strip(",") for x in plaintiff.split()]
    d_l = [x.strip(",") for x in defendant.split()]
    # Build word pairs to match
    ap_l = [x for x in itertools.product(a_l, p_l)]
    ad_l = [x for x in itertools.product(a_l, d_l)]
    # Calculate full matches
    # pj = [len(j) for j in [set(i) for i in ap_l]].count(1)
    # dj = [len(j) for j in [set(i) for i in ad_l]].count(1)
    # Calculate fuzzy matches (>THRES)
    pj = list(map(lt, list(map(fuzzy, ap_l))))
    dj = list(map(lt, list(map(fuzzy, ad_l))))
    pj = sum(pj)
    dj = sum(dj)
    return (pj, dj)


def match_disposition(
    awarded_against, awarded_to, plaintiff, defendant, disposition_type, status
):
    """The function to figure out who judgement is for"""
    if status is not None:
        if "Dismissed" in status:  #
            return (100, "No Judgement")
        if "DWOP" in status:  #
            return (100, "No Judgement")
    if disposition_type is not None:
        if "Dismissed" in disposition_type:  #
            return (100, "No Judgement")
        if "Default" in disposition_type:
            return (100, "Plaintiff")
    if (
        awarded_to is not None and plaintiff is not None and defendant is not None
    ):  # awarded_to and awarded_against will always be not None together
        #  dj = fuzz.partial_ratio(awarded_to.upper(),defendant.upper())
        #  pj = fuzz.partial_ratio(awarded_to.upper(),plaintiff.upper())
        pj, dj = match_wordwise(
            awarded_to.upper(), plaintiff.upper(), defendant.upper()
        )
        if pj > dj:
            return (pj, "Plaintiff")
        elif dj > pj:
            return (dj, "Defendant")
        else:
            pj, dj = match_wordwise(
                awarded_against.upper(), plaintiff.upper(), defendant.upper()
            )
            if pj < dj:
                return (pj, "Plaintiff")
            elif dj < pj:
                return (dj, "Defendant")
    return (None, None)


def active_or_inactive(status):
    status = status.lower()
    if status in statuses_map:
        return "Active" if statuses_map[status]["is_active"] else "Inactive"
    else:
        log_and_email(
            f"Can't figure out whether case with substatus '{status}' is active or inactive because '{status}' is not in our statuses map dictionary.",
            "Encountered Unknown Substatus",
            error=True,
        )
        return ""


def judgment_after_moratorium(disposition_date, substatus):
    substatus = substatus.lower()
    if (not disposition_date) or (substatus not in statuses_map):
        return ""

    disposition_date = datetime.strptime(disposition_date, "%m/%d/%Y")
    march_14 = datetime(2020, 3, 14)

    return (
        "Y"
        if (
            (disposition_date >= march_14)
            and (statuses_map[substatus]["status"] == "Judgment")
        )
        else "N"
    )


def make_parsed_case(
    soup, status: str = "", type: str = "", register_url: str = ""
) -> Dict[str, str]:
    # TODO handle multiple defendants/plaintiffs with different zips
    disposition_tr = get_disposition_tr_element(soup)

    try:
        defendant_zip = get_zip(get_defendant_elements(soup)[0])
    except:
        defendant_zip = None

    try:
        style = get_style(soup)
    except:
        style = None

    try:
        plaintiff = get_plaintiff(soup)
    except:
        plaintiff = None

    try:
        plaintiff_zip = get_zip(get_plaintiff_elements(soup)[0])
    except:
        plaintiff_zip = None

    try:
        disp_type = get_disposition_type(disposition_tr)
    except:
        disp_type = None

    try:
        score, winner = match_disposition(
            get_disposition_awarded_against(disposition_tr),
            get_disposition_awarded_to(disposition_tr),
            plaintiff,
            get_defendants(soup),
            disp_type,
            status,
        )
    except Exception as e:
        print(e)
        score, winner = None, None

    disposition_date = get_disposition_date(disposition_tr)
    return {
        "precinct_number": get_precinct_number(soup),
        "style": style,
        "plaintiff": plaintiff,
        "active_or_inactive": active_or_inactive(status),
        "judgment_after_moratorium": judgment_after_moratorium(
            disposition_date, status
        ),
        "defendants": get_defendants(soup),
        "attorneys_for_plaintiffs": ", ".join(
            [a for a in get_attorneys_for_plaintiffs(soup)]
        ),
        "attorneys_for_defendants": ", ".join(
            [a for a in get_attorneys_for_defendants(soup)]
        ),
        "case_number": get_case_number(soup),
        "defendant_zip": defendant_zip,
        "plaintiff_zip": plaintiff_zip,
        "hearings": [
            make_parsed_hearing(hearing) for hearing in get_hearing_tags(soup)
        ],
        "status": status,
        "type": type,
        "register_url": register_url,
        "disposition_type": get_disposition_type(disposition_tr)
        if disp_type is not None
        else "",
        "disposition_amount": get_disposition_amount(disposition_tr)
        if disposition_tr is not None
        else "",
        "disposition_date": disposition_date if disposition_tr is not None else "",
        "disposition_awarded_to": get_disposition_awarded_to(disposition_tr)
        if get_disposition_awarded_to(disposition_tr) is not None
        else "",
        "disposition_awarded_against": get_disposition_awarded_against(disposition_tr)
        if get_disposition_awarded_against(disposition_tr) is not None
        else "",
        "comments": get_comments(soup) if get_comments(soup) is not None else "",
        "writ": get_writ(soup),
        "writ_of_possession_service": get_writ_of_possession_service(soup),
        "writ_of_possession_requested": get_writ_of_possession_requested(soup),
        "writ_of_possession_sent_to_constable_office": get_writ_of_possession_sent_to_constable(
            soup
        ),
        "writ_returned_to_court": get_writ_returned_to_court(soup),
        "judgement_for": winner if winner is not None else "",
        "match_score": score if score is not None else "",
        "date_filed": get_date_filed(soup),
    }


def get_setting(soup) -> Optional[Dict[str, str]]:
    "get setting as a dict from a row of the table"
    setting_details: Dict[str, str] = {}
    td_list = soup.find_all("td")

    # get case number
    try:
        setting_details["case_number"] = td_list[1].text
    except:
        return None

    # get case link
    try:
        setting_details["case_link"] = td_list[1].find("a").get("href")
    except:
        setting_details["case_link"] = ""

    # get setting type
    try:
        setting_details["setting_type"] = td_list[2].text
    except:
        setting_details["setting_type"] = ""

    # get setting style
    try:
        setting_details["setting_style"] = td_list[3].text
    except:
        setting_details["setting_style"] = ""

    # get judicial officer
    try:
        setting_details["judicial_officer"] = td_list[4].text
    except:
        setting_details["judicial_officer"] = ""

    # get setting date
    try:
        setting_details["setting_date"] = td_list[8].text
    except:
        setting_details["setting_date"] = ""

    # get setting time
    try:
        setting_details["setting_time"] = td_list[9].text
    except:
        setting_details["setting_time"] = ""

    # get hearing type
    try:
        setting_details["hearing_type"] = td_list[10].text
    except:
        setting_details["hearing_type"] = ""
    return setting_details


def get_setting_list(calendar_soup) -> List[Optional[Dict[str, str]]]:
    "gets all settings from calendar soup table, as a list of dicts"
    # get all tables
    table_list = calendar_soup.find_all("table")

    # return first table containing string "Judicial Officer" (there may be a better way to do this)
    officer_table_list = [
        table
        for table in table_list
        if table.find("td", text="Judicial Officer") is not None
    ]
    settings_table = officer_table_list[0]

    # get the header row, and all next siblings as a list
    header_row = settings_table.find_all("tr")[0]
    tablerow_list = header_row.find_next_siblings("tr")
    if len(tablerow_list) == 0:
        return []

    # go row by row, get setting
    setting_list = []
    for tablerow in tablerow_list:
        setting = get_setting(tablerow)
        if setting is not None:
            setting_list.append(get_setting(tablerow))
    return setting_list


def get_filing_case_nums(filing_soup) -> Tuple[List[str], bool]:
    "returns list of case numbers given soup of search results"
    # get all tables
    table_list = filing_soup.find_all("table")

    # get first table containing string "Filed/Location" in a header (get the main table of the page)
    filings_table = [
        table
        for table in table_list
        if table.find("th", text="Filed/Location") is not None
    ][0]

    query_needs_splitting = False

    # get the header row, and all next siblings as a list
    header_row = filings_table.find_all("tr")[0]
    tablerow_list = header_row.find_next_siblings("tr")

    # go row by row, get case number
    case_nums = []
    for tablerow in tablerow_list:
        if "too many matches to display" in tablerow.text:
            logger.warning("Case number query had too many matches, will be split")
            query_needs_splitting = True
            break
        try:
            td_list = tablerow.find_all("td")
            # uncomment and indent next 3 lines if you want only evictions
            # if "Eviction" in td_list[3].text:
            case_num = td_list[0].text
            if case_num is not None:
                case_nums.append(case_num)
        except:
            logger.error(f"Couldn't get case number for row {tablerow}")

    # handle case of no results
    if (len(case_nums) == 1) and ("No cases matched" in case_nums[0]):
        case_nums = []

    return case_nums, query_needs_splitting


def split_date_range(afterdate: str, beforedate: str) -> Tuple[str, str]:
    """
    Split date range in half.

    Requires inputs in format m-d-y.
    Returns 4 strings representing two new date ranges
    """

    beforedate_date = datetime.strptime(afterdate, "%m-%d-%Y").date()
    afterdate_date = datetime.strptime(beforedate, "%m-%d-%Y").date()

    if beforedate_date == afterdate_date:
        raise ValueError(
            "split_date_range function was called with the same beforedate and afterdate."
        )

    time_between_dates = beforedate_date - afterdate_date
    days_to_add = (time_between_dates / 2).days

    end_of_first_range_date = afterdate_date + timedelta(days=days_to_add)
    start_of_second_range_date = end_of_first_range_date + timedelta(days=1)

    # https://stackoverflow.com/a/2073189/15014986
    # To remove leading zeroes, we use '-' on Linux and '#' on Windows. Just check for both.
    try:
        # For Linux
        end_of_first_range = end_of_first_range_date.strftime("%-m-%-d-%Y")
        start_of_second_range = start_of_second_range_date.strftime("%-m-%-d-%Y")
    except ValueError:
        # For Windows
        end_of_first_range = end_of_first_range_date.strftime("%#m-%#d-%Y")
        start_of_second_range = start_of_second_range_date.strftime("%#m-%#d-%Y")

    return end_of_first_range, start_of_second_range
