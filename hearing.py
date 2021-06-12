"""Module for scraping hearing information"""
from decimal import Decimal
import re
import sys
import itertools
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import datetime
import logging

from cases import EvictionHearing, CaseEvent, EvictionCase
from statuses import statuses_map
from fuzzywuzzy import fuzz
from emailing import log_and_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout)


class BaseParser:
    def get_plaintiff(self, soup):
        # TODO handle multiple plaintiffs
        tag = self.get_plaintiff_elements(soup)[0]
        name_elem = tag.find_next_sibling("th")

        return name_elem.text.strip()

    def get_plaintiff_elements(self, soup):
        """
        Gets the plaintiff HTML elements from a CaseDetail.
        These are currently used as an anchor for most of the Party Info parsing.
        """
        return soup.find_all("th", text=re.compile(r"Plaintiff"))

    def get_defendant_elements(self, soup):
        """
        Gets the defendant HTML elements from a CaseDetail.
        These are currently used as an anchor for most of the Party Info parsing.
        Sometimes the text of the element does not always say "Defendant", but may say something like "Defendant 2".
        """
        return soup.find_all("th", text=re.compile(r"^Defendant"))

    def get_defendants(self, soup) -> str:
        defendants = []
        for tag in self.get_defendant_elements(soup):
            name_elem = tag.find_next_sibling("th")
            defendants.append(name_elem.text.strip())
        together = "; ".join(defendants)
        return together

    def get_attorneys_header_id(self, soup: BeautifulSoup) -> Optional[str]:
        """Get the HTML ID attribute for the "Attorneys" column header."""
        element = soup.find("th", text="Attorneys")
        if not element:
            return None

        return element.get("id")

    def get_attorneys_for_party(
        self, soup: BeautifulSoup, party_elements
    ) -> Dict[str, List[str]]:
        """Get the attorney(s) for a party."""
        attorneys: Dict[str, List[str]] = dict()
        attorneys_header_id = self.get_attorneys_header_id(soup)

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

    def get_attorneys_for_defendants(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Get the attorney(s) for the defendant(s)."""
        defendant_elements = self.get_defendant_elements(soup)
        return self.get_attorneys_for_party(soup, defendant_elements)

    def get_attorneys_for_plaintiffs(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Get the attorney(s) for the plaintiff(s)."""
        plaintiff_elements = self.get_plaintiff_elements(soup)
        return self.get_attorneys_for_party(soup, plaintiff_elements)

    def get_case_number(self, soup) -> str:
        elem = soup.find(class_="ssCaseDetailCaseNbr").span
        return elem.text

    def get_style(self, soup) -> str:
        elem = soup.find_all("table")[4].tbody.tr.td
        return elem.text.strip()

    def get_date_filed(self, soup: BeautifulSoup) -> str:
        """Get date filed for the case filing."""
        elem = soup.find_all("table")[4].find("th", text="Date Filed:").find_next("b")
        return elem.text

    def get_zip(self, party_info_th_soup) -> str:
        """Returns a ZIP code from the Table Heading Party Info of a CaseDetail"""
        zip_regex = re.compile(r", \w{2} \d{5}(-\d{4})?")

        def has_zip(string: str) -> bool:
            return bool(zip_regex.search(string.lower()))

        zip_tag = party_info_th_soup.find_next(string=has_zip)
        return zip_tag.strip().split()[-1] if zip_tag is not None else ""

    def get_disposition_tr_element(self, soup) -> str:
        """
        Returns the <tr> element of a CaseDetail document that contains Disposition info, if one exists.
        """
        disp_date_th = soup.find(
            "th", id=lambda id_str: id_str is not None and "RDISPDATE" in id_str
        )
        return disp_date_th.parent if disp_date_th is not None else None

    def get_disposition_type(self, disposition_tr) -> str:
        if disposition_tr:
            return disposition_tr.find("b").text
        return ""

    def get_disposition_awarded_to(self, disposition_tr) -> str:
        """
        Gets the "Awarded To" field of a disposition, if one exists.
        """
        if disposition_tr is None:
            return ""

        award_field = disposition_tr.find(text=re.compile(r"Awarded To:"))

        if award_field is None:
            return ""

        return award_field.next_sibling.text.strip()

    def get_disposition_awarded_against(self, disposition_tr) -> str:
        """
        Gets the "Awarded Against" field of a disposition, if one exists.
        """
        if disposition_tr is None:
            return ""

        award_field = disposition_tr.find(text=re.compile(r"Awarded Against:"))

        if award_field is None:
            return ""

        return award_field.next_sibling.text.strip()

    def get_events_tbody_element(self, soup):
        """
        Returns the <tbody> element  of a CaseDetail document
        that contains Dispositions, Hearings, and Other Events.
        Used as a starting point for many event parsing methods.
        """
        table_caption_div = soup.find(
            "div",
            class_="ssCaseDetailSectionTitle",
            text=re.compile(r"\s*Events & Orders of the Court\s*"),
        )
        tbody = table_caption_div.parent.find_next_sibling("tbody")
        return tbody

    def get_hearing_tags(self, soup) -> List:
        """
        Returns <tr> elements in the Events and Hearings section of a CaseDetail document that represent a hearing record.
        """
        root = self.get_events_tbody_element(soup)
        hearing_ths = root.find_all(
            "th", id=lambda id_str: id_str is not None and id_str.startswith("RCDHR")
        )
        hearing_trs = [hearing_th.parent for hearing_th in hearing_ths]

        return hearing_trs or []

    def get_hearing_and_event_tags(self, soup) -> List:
        """
        Returns <tr> elements in the Events and Hearings section of a CaseDetail document.
        """
        root = self.get_events_tbody_element(soup)
        hearing_or_event_ths = root.find_all(
            "th", id=lambda id_str: id_str is not None and id_str.startswith("RCD")
        )
        hearing_or_event_trs = [
            hearing_th.parent for hearing_th in hearing_or_event_ths
        ]

        return hearing_or_event_trs or []

    def get_hearing_text(self, hearing_tag) -> str:
        return hearing_tag.find("b").next_sibling if hearing_tag is not None else ""

    def get_hearing_date(self, hearing_tag) -> str:
        if hearing_tag is None:
            return ""
        date_tag = hearing_tag.find("th")
        return date_tag.text if date_tag else ""

    def get_hearing_type_from_hearing_tag(self, hearing_tag) -> str:
        hearings = hearing_tag.find_all("b")
        if any(hearings):
            return hearings[0].text
        return ""

    def get_all_text_from_hearing_tag(self, hearing_tag) -> str:
        all_tds = hearing_tag.find_all("td")
        all_text = all_tds[-1].get_text(separator=" ")

        if not all_text:
            for td in all_tds:
                text = td.get_text(separator=" ")
                if len(text) > 1 and text not in all_text:
                    all_text += text

        return all_text

    def get_hearing_time(self, hearing_tag) -> str:
        hearing_text = self.get_hearing_text(hearing_tag)
        hearing_time_matches = re.search(r"\d{1,2}:\d{2} [AP]M", hearing_text)
        return hearing_time_matches[0] if hearing_time_matches is not None else ""

    def remove_whitespace(self, text: str) -> str:
        result = text.replace("\n", "").strip(") ")
        while "  " in result:
            result = result.replace("  ", " ")
        return result.strip()

    def get_hearing_officer(self, hearing_tag) -> str:
        hearing_text = self.get_hearing_text(hearing_tag)
        cleaned_hearing_text = self.remove_whitespace(hearing_text)
        officer_groups = cleaned_hearing_text.split("Judicial Officer")
        name = officer_groups[1] if len(officer_groups) > 1 else ""
        return self.remove_whitespace(name)

    def get_disposition_date_node(self, soup) -> Optional[BeautifulSoup]:
        return soup.find("th", id=re.compile(r"RDISPDATE1")) if soup else None

    def get_disposition_date(self, soup: Optional[BeautifulSoup]) -> Optional[str]:
        if soup is None:
            return None
        disposition_date_node = self.get_disposition_date_node(soup)
        if disposition_date_node:
            return self.remove_whitespace(disposition_date_node.text)
        return None

    def read_disposition_amount_text(self, text: str) -> Optional[Decimal]:
        if "$" not in text:
            return None
        amount_as_string = text.strip(". ")
        amount = Decimal(re.sub(r"[^\d.]", "", amount_as_string))
        return amount

    def get_disposition_amount(self, soup) -> Optional[Decimal]:
        disposition_date_node = self.get_disposition_date_node(soup)
        if disposition_date_node is None:
            return None
        disposition_label = disposition_date_node.find_next_sibling(
            "td", headers="CDisp RDISPDATE1"
        )
        disposition_amount_node = disposition_label.find("nobr")
        if disposition_amount_node is None:
            return None
        return self.read_disposition_amount_text(disposition_amount_node.text)

    def get_precinct_number(self, soup) -> int:
        word_to_number = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

        location_heading = soup.find(text="Location:").parent
        precinct_name = location_heading.find_next_sibling("td").text
        precinct_number = precinct_name.split("Precinct ")[1]

        return word_to_number[precinct_number]

    def get_comments(self, soup: BeautifulSoup) -> Optional[str]:
        """Get comments from case page."""

        disposition_date_node = self.get_disposition_date_node(soup)
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

    def make_case_event_from_date_string(self, case_event_date: str) -> datetime.date:
        try:
            return datetime.datetime.strptime(case_event_date, "%m/%d/%Y").date()
        except TypeError:
            return case_event_date

    def get_case_event_date_basic(
        self, soup: BeautifulSoup, event_name: str
    ) -> Optional[datetime.date]:
        """Get date for case event entries that only include event name."""
        case_event_date: Optional[str] = None

        case_events = self.get_events_tbody_element(soup)
        event_label = case_events.find("b", text=event_name)
        if event_label:
            try:
                case_event_tr = event_label.parent.parent
                case_event_date = case_event_tr.find(
                    "th", class_="ssTableHeaderLabel"
                ).text
            except AttributeError:
                return None

        return self.make_case_event_from_date_string(case_event_date=case_event_date)

    def get_writ_issued_date(self, event_tr) -> Optional[datetime.date]:

        if event_tr:
            try:
                text = event_tr.find("th", class_="ssTableHeaderLabel").text
                return datetime.strpime(text.strip(), format="%m/%d/%Y")
            except AttributeError:
                return text
        return None

    def get_writ_served_date(self, served_td) -> str:
        try:
            return served_td.find_next_sibling("td").text
        except AttributeError:
            return ""

    def get_writ_served_subject(self, served_td) -> str:
        try:
            elem = served_td.parent.parent.parent.parent
            return elem.find_previous_sibling("td").text
        except AttributeError:
            return ""

    def get_writ_returned(self, returned_td) -> str:
        try:
            return returned_td.find_next_sibling("td").text
        except AttributeError:
            return ""

    def get_writ(self, soup: BeautifulSoup) -> Optional[CaseEvent]:
        """Get details for the "Writ" case event."""

        case_events = self.get_events_tbody_element(soup)
        event_label = case_events.find("b", text="Writ")
        if not event_label:
            return None

        event_tr = event_label.parent.parent.parent.parent.parent.parent
        served_td = event_tr.find("td", text="Served")
        returned_td = event_tr.find("td", text="Returned")
        return CaseEvent(
            case_event_date=self.get_writ_issued_date(event_tr=event_tr),
            served_date=self.get_writ_served_date(served_td),
            served_subject=self.get_writ_served_subject(served_td),
            returned=self.get_writ_returned(returned_td),
        )

    def get_writ_of_possession_service(
        self, soup: BeautifulSoup
    ) -> Optional[CaseEvent]:
        """Get details for the "Writ of Possession Service" case event."""

        event_date = self.get_case_event_date_basic(soup, "Writ of Possession Service")
        return CaseEvent(case_event_date=event_date) if event_date else None

    def get_writ_of_possession_requested(
        self, soup: BeautifulSoup
    ) -> Optional[CaseEvent]:
        """Get details for the "Writ of Possession Requested" case event."""
        event_date = self.get_case_event_date_basic(
            soup, "Writ of Possession Requested"
        )
        return CaseEvent(case_event_date=event_date) if event_date else None

    def get_writ_of_possession_sent_to_constable(
        self, soup: BeautifulSoup
    ) -> Optional[CaseEvent]:
        """Get details for the "Writ of Possession Sent to Constable's Office" case event."""
        event_date = self.get_case_event_date_basic(
            soup, "Writ of Possession Sent to Constable's Office"
        )
        return CaseEvent(case_event_date=event_date) if event_date else None

    def get_writ_returned_to_court(self, soup: BeautifulSoup) -> Optional[CaseEvent]:
        """Get details for the "Writ Returned to Court" case event."""
        event_date = self.get_case_event_date_basic(soup, "Writ Returned to Court")
        if not event_date:
            event_date = self.get_case_event_date_basic(soup, "Writ Returned")
        return CaseEvent(case_event_date=event_date) if event_date else None

    def did_defendant_appear(self, hearing_tag) -> bool:
        """If "appeared" appears, infer defendant appeared."""

        if hearing_tag is None:
            return False

        def appeared_in_text(text):
            return text and re.compile("[aA]ppeared").search(text)

        appeared_tag = hearing_tag.find(text=appeared_in_text)
        return appeared_tag is not None

    def was_defendant_served(self, soup) -> List[str]:
        dates_of_service = {}
        served_tags = soup.find_all(text="Served")
        for service_tag in served_tags:
            date_tag = service_tag.parent.find_next_sibling("td")
            defendant_tag = (
                service_tag.parent.parent.parent.parent.parent.find_previous_sibling(
                    "td"
                )
            )
            if defendant_tag.text not in dates_of_service:
                dates_of_service[defendant_tag.text] = date_tag.text

        return dates_of_service

    def was_defendant_alternative_served(self, soup) -> List[str]:
        dates_of_service = []
        served_tags = soup.find_all(text="Order Granting Alternative Service")
        for service_tag in served_tags:
            date_tag = service_tag.parent.parent.find_previous_sibling("th")
            dates_of_service.append(date_tag.text)

        return dates_of_service

    def make_parsed_hearing(self, soup):

        try:
            time = self.get_hearing_time(soup)
        except:
            time = ""

        try:
            officer = self.get_hearing_officer(soup)
        except:
            officer = ""

        try:
            appeared = self.did_defendant_appear(soup)
        except:
            appeared = None

        hearing_type = self.get_hearing_type_from_hearing_tag(soup)

        all_text = self.get_all_text_from_hearing_tag(soup)

        return EvictionHearing(
            hearing_date=self.get_hearing_date(soup),
            hearing_time=time,
            hearing_officer=officer,
            appeared=appeared,
            hearing_type=hearing_type,
            all_text=all_text,
        )

    THRESH = 75

    def lt(self, i):
        if i > self.THRESH:
            return i
        else:
            return 0

    def fuzzy(self, i):
        j = fuzz.partial_ratio(i[0].upper(), i[1].upper())
        return j

    def match_wordwise(self, awarded_to, plaintiff, defendant):
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
        pj = list(map(self.lt, list(map(self.fuzzy, ap_l))))
        dj = list(map(self.lt, list(map(self.fuzzy, ad_l))))
        pj = sum(pj)
        dj = sum(dj)
        return (pj, dj)

    def match_disposition(
        self,
        awarded_against,
        awarded_to,
        plaintiff,
        defendant,
        disposition_type,
        status,
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
            pj, dj = self.match_wordwise(
                awarded_to.upper(), plaintiff.upper(), defendant.upper()
            )
            if pj > dj:
                return (pj, "Plaintiff")
            elif dj > pj:
                return (dj, "Defendant")
            else:
                pj, dj = self.match_wordwise(
                    awarded_against.upper(), plaintiff.upper(), defendant.upper()
                )
                if pj < dj:
                    return (pj, "Plaintiff")
                elif dj < pj:
                    return (dj, "Defendant")
        return (None, None)

    def active_or_inactive(self, status) -> str:
        status = status.lower()
        if status in statuses_map:
            return "Active" if statuses_map[status]["is_active"] else "Inactive"

        log_and_email(
            f"Can't figure out whether case with substatus '{status}' is active or inactive "
            f"because '{status}' is not in our statuses map dictionary.",
            "Encountered Unknown Substatus",
            error=True,
        )
        return ""

    def judgment_after_moratorium(self, disposition_date, substatus):
        substatus = substatus.lower()
        if (not disposition_date) or (substatus not in statuses_map):
            return ""

        disposition_date = datetime.strptime(disposition_date, "%m/%d/%Y")
        march_14 = datetime.date(2020, 3, 14)

        return (
            "Y"
            if (
                (disposition_date >= march_14)
                and (statuses_map[substatus]["status"] == "Judgment")
            )
            else "N"
        )

    def make_parsed_case(
        self, soup, status: str = "", type: str = "", register_url: str = ""
    ) -> EvictionCase:
        # TODO handle multiple defendants/plaintiffs with different zips
        disposition_tr = self.get_disposition_tr_element(soup)

        try:
            defendant_zip = self.get_zip(self.get_defendant_elements(soup)[0])
        except:
            defendant_zip = ""

        try:
            style = self.get_style(soup)
        except:
            style = ""

        try:
            plaintiff = self.get_plaintiff(soup)
        except:
            plaintiff = ""

        try:
            plaintiff_zip = self.get_zip(self.get_plaintiff_elements(soup)[0])
        except:
            plaintiff_zip = ""

        try:
            disp_type = self.get_disposition_type(disposition_tr)
        except AttributeError:
            disp_type = ""

        try:
            score, winner = self.match_disposition(
                self.get_disposition_awarded_against(disposition_tr),
                self.get_disposition_awarded_to(disposition_tr),
                plaintiff,
                self.get_defendants(soup),
                disp_type,
                status,
            )
        except Exception as e:
            print(e)
            score, winner = None, None

        defendants = self.get_defendants(soup)

        disposition_date = self.get_disposition_date(disposition_tr)
        return EvictionCase(
            precinct_number=self.get_precinct_number(soup),
            style=style,
            plaintiff=plaintiff,
            active_or_inactive=self.active_or_inactive(status),
            judgment_after_moratorium=self.judgment_after_moratorium(
                disposition_date, status
            ),
            defendants=defendants,
            attorneys_for_plaintiffs=", ".join(
                [a for a in self.get_attorneys_for_plaintiffs(soup)]
            ),
            attorneys_for_defendants=", ".join(
                [a for a in self.get_attorneys_for_defendants(soup)]
            ),
            case_number=self.get_case_number(soup),
            defendant_zip=defendant_zip,
            plaintiff_zip=plaintiff_zip,
            hearings=[
                self.make_parsed_hearing(hearing)
                for hearing in self.get_hearing_tags(soup)
            ],
            status=status,
            type=type,
            register_url=register_url or None,
            disposition_type=self.get_disposition_type(disposition_tr)
            if disp_type is not None
            else "",
            disposition_amount=self.get_disposition_amount(disposition_tr),
            disposition_date=disposition_date if disposition_tr is not None else "",
            disposition_awarded_to=self.get_disposition_awarded_to(disposition_tr),
            disposition_awarded_against=self.get_disposition_awarded_against(
                disposition_tr
            )
            if self.get_disposition_awarded_against(disposition_tr) is not None
            else "",
            comments=self.get_comments(soup)
            if self.get_comments(soup) is not None
            else "",
            writ=self.get_writ(soup),
            writ_of_possession_service=self.get_writ_of_possession_service(soup),
            writ_of_possession_requested=self.get_writ_of_possession_requested(soup),
            writ_of_possession_sent_to_constable_office=self.get_writ_of_possession_sent_to_constable(
                soup
            ),
            writ_returned_to_court=self.get_writ_returned_to_court(soup),
            judgement_for=winner if winner is not None else "",
            match_score=score if score is not None else "",
            date_filed=self.get_date_filed(soup),
        )


class HaysParser(BaseParser):
    def get_defendant_elements(self, soup):
        """
        Gets the defendant HTML elements from a CaseDetail.
        These are currently used as an anchor for most of the Party Info parsing.
        Sometimes the text of the element does not always say "Defendant", but may say something like "Defendant 2".
        """
        return soup.find_all("th", text=re.compile(r"Defendant"))

    def get_precinct_number(self, soup) -> int:
        location_heading = soup.find(text=re.compile("Location:")).parent
        precinct_name = location_heading.find_next_sibling("td").text
        precinct_name = float(precinct_name[2:])  # get rid of JP
        return precinct_name

    def get_disposition_amt_node(self, soup) -> BeautifulSoup:
        try:
            return soup.find("th", id="")
        except:
            return None

    def get_disposition_amount(self, soup) -> Optional[Decimal]:
        """get the disposition amount for hays county"""
        amt_tags = soup.find_all("i")
        for tag in amt_tags:
            if tag.text.lower().startswith(
                "amt",
            ):
                return self.read_disposition_amount_text(tag.text)
        return None

    def get_attorneys_header_id(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Get the HTML ID attribute for the
        "Lead Attorneys" column header.
        """
        element = soup.find("th", text="Lead Attorneys")
        if not element:
            return None

        return element.get("id")

    def get_defendant_info_tags(self, soup: BeautifulSoup):
        """Helper function to get defendant info tags"""
        def_info_tags = soup.find_all("td", headers=re.compile(r"\s*PIr01\s*PIr11"))
        return def_info_tags

    def get_defendant_address(self, soup: BeautifulSoup) -> str:
        """Get address for defendant"""
        def_info_tag = self.get_defendant_info_tags(soup)[2]
        address = def_info_tag.text.split("\xa0\xa0")
        # only take 1st element will it always have a leading " " (actually a \xa0)?
        address = " ".join(address[1:]).split(" SID")[0]  # no SID info if its in there
        return address

    def get_defendant_race_gender(self, soup: BeautifulSoup):
        """Get race and gender info for defendant"""
        def_info_tag = self.get_defendant_info_tags(soup)[0]
        race_gender = def_info_tag.text.split("\n")[0]

        return race_gender.split(" ")

    def get_defendant_race(self, soup: BeautifulSoup) -> str:
        race = " ".join(self.get_defendant_race_gender(soup)[1:])
        return race

    def get_defendant_gender(self, soup: BeautifulSoup) -> str:
        categories = self.get_defendant_race_gender(soup)
        return categories[0] if categories else ""

    def was_defendant_alternative_served(self, soup) -> List[str]:
        """Just allows a different label for "Order Granting Alternative Service"."""
        dates_of_service = super().was_defendant_alternative_served(soup)
        served_tags = soup.find_all(text="Order For Substituted Service")
        for service_tag in served_tags:
            date_tag = service_tag.parent.parent.find_previous_sibling("th")
            dates_of_service.append(date_tag.text)

        return dates_of_service

    def get_writ_of_possession_requested(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Get details for the "Writ of Possession Requested" case event.

        Assumes that an element with id "RCDER12" must contain the date
        of this request.
        """
        event_details = super().get_writ_of_possession_requested(soup=soup)
        if event_details:
            return event_details

        request_date_element = soup.find(id="RCDER12")
        if request_date_element and request_date_element.text:
            event_details["case_event_date"] = request_date_element.text.strip()

        return event_details

    def get_writ_issued_date(self, event_tr) -> Optional[str]:
        issued_date_element = event_tr.find(id=["RCDER13", "RCDSE13", "RCDER14"])
        if issued_date_element and issued_date_element.text.strip():
            text = issued_date_element.text.strip()
            return datetime.datetime.strptime(text.strip(), "%m/%d/%Y")

        return None

    def get_writ_of_possession_service(
        self, soup: BeautifulSoup
    ) -> Optional[CaseEvent]:
        """
        Get details for the "Writ of Possession Requested" case event.

        Assumes that an element with id "RCDER12" must contain the date
        of this request.
        """
        event_details = super().get_writ_of_possession_requested(soup=soup)
        if event_details:
            return event_details

        request_date_element = soup.find(id=["RCDSE14", "RCDSE15"])
        if request_date_element.text:
            return self.make_case_event_from_date_string(
                request_date_element.text.strip()
            )
        return None

    def make_parsed_case(
        self, soup, status: str = "", type: str = "", register_url: str = ""
    ) -> EvictionCase:

        try:
            address = self.get_defendant_address(soup)
        except AttributeError:
            address = ""

        parsed_case = super().make_parsed_case(
            soup=soup, status=status, type=type, register_url=register_url
        )
        parsed_case.defendant_address = address
        parsed_case.defendant_race = self.get_defendant_race(soup)
        parsed_case.defendant_gender = self.get_defendant_gender(soup)

        return parsed_case


class WilliamsonParser(BaseParser):
    def get_all_text_from_hearing_tag(self, hearing_tag) -> str:

        all_text = self.remove_whitespace(hearing_tag.text)
        return all_text

    def get_attorneys_header_id(self, soup: BeautifulSoup) -> Optional[str]:
        """Get the HTML ID attribute for the "Attorneys" column header."""
        element = soup.find("th", text="Lead Attorneys")
        if not element:
            return None

        return element.get("id")

    def get_defendant_elements(self, soup):
        """
        Gets the defendant HTML elements from a CaseDetail.
        These are currently used as an anchor for most of the Party Info parsing.
        Sometimes the text of the element does not always say "Defendant", but may say something like "Defendant 2".
        """
        return soup.find_all("th", text=re.compile(r"^\s*Defendant"))

    def get_events_tbody_element(self, soup):
        """
        Returns the <tbody> element  of a CaseDetail document
        that contains Dispositions, Hearings, and Other Events.
        Used as a starting point for many event parsing methods.
        """
        table_caption = soup.find_all("caption")[1]
        try:
            tbody = table_caption.find_next_sibling("tr").find_next_sibling("tr")
            return tbody
        except AttributeError:
            return super().get_events_tbody_element(soup)

    def get_hearing_date(self, hearing_tag) -> str:
        if hearing_tag is None:
            return ""
        date_tag = hearing_tag.parent.th
        text = date_tag.text
        return self.remove_whitespace(text)

    def get_hearing_tags(self, soup) -> List:
        """
        Returns <tr> elements in the Events and Hearings section of a CaseDetail document that represent a hearing record.
        """
        root = self.get_events_tbody_element(soup).parent
        hearing_tds = root.find_all(
            "td",
            headers=lambda id_str: id_str is not None and id_str.startswith("RCDHR"),
        )

        return hearing_tds or []

    def get_hearing_and_event_tags(self, soup) -> List:
        """
        Returns <tr> elements in the Events and Hearings section representing a hearing record.
        """
        root = self.get_events_tbody_element(soup).parent
        hearing_tds = root.find_all(
            "td",
            headers=lambda id_str: id_str is not None and id_str.startswith("RCD"),
        )

        return hearing_tds or []

    def get_precinct_number(self, soup) -> int:
        location_heading = soup.find(text="Location:").parent
        precinct_name = location_heading.find_next_sibling("td").text
        return int(precinct_name[-1])

    def get_style(self, soup):
        """Get name of the case."""
        tables = soup.find_all("table")
        elem = tables[4].tr.td.b
        return self.remove_whitespace(elem.text)

    def get_defendant_tag_for_service_tag(self, service_tag):
        defendant_tag = service_tag.parent.parent.parent.parent.parent.td
        if self.remove_whitespace(defendant_tag.text) != "Served":
            return defendant_tag
        return service_tag.parent.parent.parent.parent.parent.parent.parent.td

    def was_defendant_served(self, soup) -> Dict[str, str]:
        dates_of_service = {}
        served_tags = soup.find_all(text="Served")
        for service_tag in served_tags:
            date_tag = service_tag.parent.find_next_sibling("td")
            defendant_tag = self.get_defendant_tag_for_service_tag(
                service_tag=service_tag
            )
            defendant_name = self.remove_whitespace(defendant_tag.text)
            dates_of_service[defendant_name] = self.remove_whitespace(date_tag.text)
        return dates_of_service
