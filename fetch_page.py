"""Module for executing searches using Selenium"""

import sys
import logging
import atexit
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from emailing import log_and_email
import hearing

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--headless")
options.add_argument("window-size=1920,1080")
options.headless = True

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)

load_dotenv()
local_dev = os.getenv("LOCAL_DEV") == "true"

if local_dev:
    driver = webdriver.Chrome("./chromedriver", options=options)
else:
    driver_path, chrome_bin = (
        os.getenv("CHROMEDRIVER_PATH"),
        os.getenv("GOOGLE_CHROME_BIN"),
    )
    options.binary_location = chrome_bin
    driver = webdriver.Chrome(executable_path=driver_path, options=options)


def close_driver():
    driver.close()


atexit.register(close_driver)


def load_start_page():
    driver.get("https://odysseypa.traviscountytx.gov/JPPublicAccess/default.aspx")
    return driver


def load_search_page():
    start_page = load_start_page()
    try:
        element = WebDriverWait(start_page, 10).until(
            EC.presence_of_element_located(
                (By.LINK_TEXT, "Civil, Family & Probate Case Records")
            )
        )
    finally:
        element.click()
        return start_page
    return None


def load_case_records_search_page():
    """Clicks into Case Records search page"""

    start_page = load_start_page()
    try:
        element = WebDriverWait(start_page, 10).until(
            EC.presence_of_element_located(
                (By.LINK_TEXT, "Civil, Family & Probate Case Records")
            )
        )
    finally:
        element.click()
        return start_page
    return None


def query_case_id(case_id: str):
    search_page = load_search_page()
    try:
        case_radio_button = WebDriverWait(search_page, 10).until(
            EC.presence_of_element_located((By.ID, "Case"))
        )
        case_radio_button.click()
    except:
        # logger.error(f"Could not click button to search for case {case_id}")
        return None

    try:
        search_box = WebDriverWait(search_page, 10).until(
            EC.presence_of_element_located((By.ID, "CaseSearchValue"))
        )
    except:
        # logger.error(f"Could not type query to search for case {case_id}")
        return None
    finally:
        search_box.send_keys(case_id)
        search_button = search_page.find_element_by_name("SearchSubmit")
        search_button.click()
        search_page.implicitly_wait(1)
        search_page_content = search_page.page_source

    try:
        register_link = WebDriverWait(search_page, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, case_id))
        )
        register_link.click()
    except:
        # logger.error(f"Could not click search result for case {case_id}")
        return None

    try:
        register_heading = WebDriverWait(search_page, 10).until(
            EC.presence_of_element_located((By.ID, "PIr11"))
        )
    except:
        # logger.error(f"Could not load register of actions for case {case_id}")
        return None
    finally:
        register_page_content = search_page.page_source
        return search_page_content, register_page_content


def load_court_calendar():
    """Opens the court calendar to scrape settings"""

    start_page = load_start_page()
    try:
        element = WebDriverWait(start_page, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Court Calendar"))
        )
    finally:
        element.click()
        return start_page
    return None


def query_settings(afterdate: str, beforedate: str):
    """Executes search for case settings between beforedate and afterdate for, returns content of resulting page"""

    for tries in range(5):
        # select Date Range radiobutton for search
        try:
            court_calendar = load_court_calendar()
            date_range_radio_button = WebDriverWait(court_calendar, 10).until(
                EC.presence_of_element_located((By.ID, "DateRange"))
            )
            date_range_radio_button.click()
            break
        except:
            logger.error(
                f"Could not click button to search settings by Date Range, try {tries}"
            )

    # deselect all Case Category checkboxes besides Civil
    for check_id in ["chkDtRangeProbate", "chkDtRangeFamily", "chkDtRangeCriminal"]:
        try:
            category_checkbox = WebDriverWait(court_calendar, 10).until(
                EC.presence_of_element_located((By.ID, check_id))
            )
            if category_checkbox.is_selected():
                category_checkbox.click()
        except:
            logger.error(f"Could not uncheck {check_id}")

    # enter before date
    try:
        after_box = WebDriverWait(court_calendar, 10).until(
            EC.presence_of_element_located((By.ID, "DateSettingOnAfter"))
        )
        after_box.clear()
        after_box.send_keys(afterdate)
    except:
        logger.error(f"Could not type in after date {afterdate}")

    # enter after date
    try:
        before_box = WebDriverWait(court_calendar, 10).until(
            EC.presence_of_element_located((By.ID, "DateSettingOnBefore"))
        )
        before_box.clear()
        before_box.send_keys(beforedate)
    except:
        logger.error(f"Could not type in before date {beforedate}")

    # click search button
    try:
        settings_link = WebDriverWait(court_calendar, 10).until(
            EC.presence_of_element_located((By.ID, "SearchSubmit"))
        )
        settings_link.click()
    except:
        logger.error(
            f"Could not click search result for dates {beforedate} {afterdate}"
        )

    finally:
        calendar_page_content = court_calendar.page_source
        return calendar_page_content


def query_filings(afterdate: str, beforedate: str, case_num_prefix: str):
    """Executes search for case filings between beforedate and afterdate for case_num_prefix, returns content of resulting page"""

    for tries in range(5):
        # select case in search by
        try:
            court_records = load_case_records_search_page()
            case_button = WebDriverWait(court_records, 10).until(
                EC.presence_of_element_located((By.ID, "Case"))
            )
            case_button.click()
            break
        except Exception as e:
            logger.error(
                f"Could not click button to search filings by Case, try {tries}"
            )

    # enter after date
    try:
        after_box = WebDriverWait(court_records, 10).until(
            EC.presence_of_element_located((By.ID, "DateFiledOnAfter"))
        )
        after_box.clear()
        after_box.send_keys(afterdate.replace("-", "/"))
    except:
        logger.error(f"Could not type in after date {afterdate}")

    # senter before date
    try:
        before_box = WebDriverWait(court_records, 10).until(
            EC.presence_of_element_located((By.ID, "DateFiledOnBefore"))
        )
        before_box.clear()
        before_box.send_keys(beforedate.replace("-", "/"))
    except Exception as e:
        logger.error(f"Could not type in before date {beforedate}")

    # type in case number prefix
    try:
        before_box = WebDriverWait(court_records, 10).until(
            EC.presence_of_element_located((By.ID, "CaseSearchValue"))
        )
        before_box.clear()
        before_box.send_keys(case_num_prefix)
    except:
        logger.error(f"Could not type in case number prefix {case_num_prefix}")

    # click search button
    try:
        settings_link = WebDriverWait(court_records, 10).until(
            EC.presence_of_element_located((By.ID, "SearchSubmit"))
        )
        settings_link.click()
    except:
        logger.error(
            f"Could not click search button for dates {afterdate} {beforedate}, prefix {case_num_prefix}"
        )

    finally:
        records_page_content = court_records.page_source
        return records_page_content


def fetch_parsed_case(case_id: str) -> Tuple[str, str]:
    query_result = query_case_id(case_id)
    if query_result is None:
        return None
    result_page, register_page = query_result
    result_soup = BeautifulSoup(result_page, "html.parser")
    register_soup = BeautifulSoup(register_page, "html.parser")

    register_url = hearing.get_register_url(result_soup)
    status, type = hearing.get_status_and_type(result_soup)

    if status.lower() not in hearing.statuses_map:
        load_dotenv()
        if os.getenv("LOCAL_DEV") != "true":
            log_and_email(
                f"Case {case_id} has status '{status}', which is not in our list of known statuses.",
                "Found Unknown Status",
                error=True,
            )
        else:
            logger.info(
                f"Case {case_id} has status '{status}', which is not in our list of known statuses."
            )

    return hearing.make_parsed_case(
        soup=register_soup, status=status, type=type, register_url=register_url
    )


def fetch_settings(afterdate: str, beforedate: str) -> [List[Optional[Dict[str, str]]]]:

    for tries in range(1, 11):
        try:
            "fetch all settings as a list of dicts"
            calendar_page_content = query_settings(afterdate, beforedate)
            if calendar_page_content is None:
                return None
            calendar_soup = BeautifulSoup(calendar_page_content, "html.parser")
            return hearing.get_setting_list(calendar_soup)
        except:
            if tries == 10:
                logger.error(
                    f"Failed to get setting list between {afterdate} and {beforedate} on all 10 attempts."
                )

    return []


def fetch_filings(afterdate: str, beforedate: str, case_num_prefix: str) -> List[str]:
    "Get filing case numbers between afterdate and beforedate and starting with case_num_prefix."

    for tries in range(1, 11):
        try:
            filings_page_content = query_filings(afterdate, beforedate, case_num_prefix)
            filings_soup = BeautifulSoup(filings_page_content, "html.parser")
            (
                filings_case_nums_list,
                query_needs_splitting,
            ) = hearing.get_filing_case_nums(filings_soup)
            break
        except:
            if tries == 10:
                logger.error(f"Failed to find case numbers on all 10 attempts.")

    # handle case of too many results (200 results means that the search cut off)
    if query_needs_splitting:
        try:
            end_of_first_range, start_of_second_range = hearing.split_date_range(
                afterdate, beforedate
            )
            filings_case_nums_list = fetch_filings(
                afterdate, end_of_first_range, case_num_prefix
            ) + fetch_filings(start_of_second_range, beforedate, case_num_prefix)
        except ValueError:
            logger.error(
                f"The search returned {len(filings_case_nums_list)} results but there's nothing "
                "the code can do because beforedate and afterdate are the same.\n"
                "Case details will be scraped for these results.\n"
            )

    # # some optional logging to make sure results look good - could remove
    # logger.info(f"Found {len(filings_case_nums_list)} case numbers.")
    # if len(filings_case_nums_list) > 5:
    #     logger.info(
    #         f"Results preview: {filings_case_nums_list[0]}, {filings_case_nums_list[1]}, "
    #         f"..., {filings_case_nums_list[-1]}\n"
    #     )
    # else:
    #     logger.info(f"Results: {', '.join(filings_case_nums_list)}\n")

    return filings_case_nums_list
