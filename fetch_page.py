import sys
import logging
import atexit
import os
from dotenv import load_dotenv
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("window-size=1920,1080")
options.headless = True

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)

load_dotenv()
local_dev = os.getenv("LOCAL_DEV") == "true"

if local_dev:
    driver = webdriver.Chrome("./chromedriver", chrome_options=options)
else:
    driver_path, chrome_bin = os.getenv('CHROMEDRIVER_PATH'), os.getenv('GOOGLE_CHROME_BIN')
    options.binary_location = chrome_bin
    driver = webdriver.Chrome(executable_path=driver_path , chrome_options=options)



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


# clicks into Case Records search page
def load_case_records_search_page():
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
        logger.error(f"Could not click button to search for case {case_id}")
        return None

    try:
        search_box = WebDriverWait(search_page, 10).until(
            EC.presence_of_element_located((By.ID, "CaseSearchValue"))
        )
    except:
        logger.error(f"Could not type query to search for case {case_id}")
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
        logger.error(f"Could not click search result for case {case_id}")
        return None

    try:
        register_heading = WebDriverWait(search_page, 10).until(
            EC.presence_of_element_located((By.ID, "PIr11"))
        )
    except:
        logger.error(f"Could not load register of actions for case {case_id}")
        return None
    finally:
        register_page_content = search_page.page_source
        return search_page_content, register_page_content


def load_court_calendar():
    # open the court calendar, to scrape Settings
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


# executes search for case filings between beforedate and afterdate for case_num_prefix, returns content of resulting page
def query_filings(afterdate: str, beforedate: str, case_num_prefix: str):
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
        after_box.send_keys(afterdate)
    except:
        logger.error(f"Could not type in after date {afterdate}")

    # senter before date
    try:
        before_box = WebDriverWait(court_records, 10).until(
            EC.presence_of_element_located((By.ID, "DateFiledOnBefore"))
        )
        before_box.clear()
        before_box.send_keys(beforedate)
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
