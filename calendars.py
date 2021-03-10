from datetime import datetime, timedelta
import logging

from typing import Dict, List, Optional, Tuple

logger = logging.getLogger()


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

    setting_list = [get_setting(tablerow) for tablerow in tablerow_list]
    return [setting for setting in setting_list if setting is not None]


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
