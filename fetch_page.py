import logging
import atexit
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logger = logging.getLogger()
driver = webdriver.Firefox()


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
