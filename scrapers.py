"""Module for scraping court websites using Selenium"""

import datetime
from itertools import chain
import logging
import os
import sys
from typing import Any, Dict, Iterator, List, NamedTuple, Optional, Tuple

import atexit
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import calendars
import case_search
import config
from emailing import log_and_email
import hearing
import load_pages


logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)


class CalendarQuery(NamedTuple):
    afterdate: datetime.date
    beforedate: datetime.date
    prefix: str


class FakeScraper:
    def __init__(self, headless: bool = True) -> None:
        self.homepage = "will not access web"

    def fetch_parsed_case(self, case_id: str) -> Tuple[str, str]:
        query_result = self.query_case_id(case_id)
        if query_result is None:
            return None
        result_soup, register_soup = query_result

        register_url = case_search.get_register_url(result_soup)
        status, type = case_search.get_status_and_type(result_soup)

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

        # TODO: choose parser based on county
        parser = hearing.BaseParser()
        return parser.make_parsed_case(
            soup=register_soup, status=status, type=type, register_url=register_url
        )

    def make_case_list(
        self, ids_to_parse: List[str], showbrowser: bool = False
    ) -> List[Dict[str, Any]]:
        """Gets case details for each case number in `ids_to_parse`"""
        parsed_cases = []

        failed_ids = []
        for id_to_parse in ids_to_parse:
            new_case = self.fetch_parsed_case(id_to_parse)
            if new_case:
                parsed_cases.append(new_case)
            else:
                failed_ids.append(id_to_parse)

        if failed_ids:
            error_message = f"Failed to scrape data for {len(failed_ids)} case numbers. Here they are:\n{', '.join(failed_ids)}"
            log_and_email(error_message, "Failed Case Numbers", error=True)

        return parsed_cases

    def calendar_queries(
        self, afterdate: datetime.date, beforedate: datetime.date
    ) -> Iterator[CalendarQuery]:
        """Make queries for court calendar to get all cases within date range."""
        years = set([afterdate.year, beforedate.year])
        for year in years:
            for prefix_text in ["J1-CV", "J2-CV", "J3-EV", "J4-CV", "J5-CV"]:
                yield CalendarQuery(
                    afterdate=afterdate,
                    beforedate=beforedate,
                    prefix=f"{prefix_text}-{year}*",
                )

    def fetch_settings(
        self, afterdate: datetime.date, beforedate: datetime.date
    ) -> List[Optional[Dict[str, str]]]:

        for tries in range(1, 11):
            try:
                "fetch all settings as a list of dicts"
                calendar_soup = self.query_settings(afterdate, beforedate)
                return calendars.get_setting_list(calendar_soup)
            except:
                if tries == 10:
                    logger.error(
                        f"Failed to get setting list between {afterdate} and {beforedate} on all 10 attempts."
                    )

        return []

    def get_all_case_nums(
        self, afterdate: datetime.date, beforedate: datetime.date
    ) -> List[str]:
        """
        Get list of all case numbers between `afterdate` and `beforedate`.
        """
        all_case_nums = []
        for query in self.calendar_queries(afterdate, beforedate):
            response = self.fetch_filings(
                query.afterdate, query.beforedate, query.prefix
            )
            all_case_nums.extend(response)

        logger.info(
            f"Scraped case numbers between {afterdate} and {beforedate} "
            f"- found {len(all_case_nums)} of them."
        )
        return all_case_nums

    def make_setting_list(self, days_to_pull: List[str]) -> List[Dict[str, Any]]:
        """Pulls all settings, one day at a time"""
        pulled_settings = []
        for setting_day in days_to_pull:
            day_settings = self.fetch_settings(
                afterdate=setting_day, beforedate=setting_day
            )
            pulled_settings.extend(day_settings)
        return pulled_settings

    def query_case_id(self, case_id: str) -> Tuple[BeautifulSoup, BeautifulSoup]:
        if case_id != "J1-CV-20-001590":
            raise ValueError(
                "The testing-only FakeScraper can only take the Case ID J1-CV-20-001590. "
                "To avoid this error use a scraper class named after a county, e.g. 'TravisScraper'"
            )
        search_page = load_pages.get_test_search_page(0)
        register_page = load_pages.get_test_soup(0)
        return search_page, register_page

    def query_settings(self, afterdate: datetime.date, beforedate: datetime.date):
        """Return fake setting list for testing."""
        if afterdate != datetime.date(2015, 10, 21):
            raise ValueError(
                "To prevent confusion between real and fake data, FakeScraper "
                "only works with date ranges "
                "that begin on 2015-10-21. To make real queries, use a scraper named "
                "for the county you want, such as 'TravisScraper'."
            )
        return load_pages.get_test_calendar()

    def fetch_filings(
        self, afterdate: datetime.date, beforedate: datetime.date, case_num_prefix: str
    ) -> List[str]:
        return ["J1-CV-20-001590"]


class TravisScraper(FakeScraper):
    def __init__(self, headless: bool = True) -> None:
        super().__init__()
        self.homepage = (
            "https://odysseypa.traviscountytx.gov/JPPublicAccess/default.aspx"
        )

        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("window-size=1920,1080")
        options.headless = headless

        if config.local_dev:
            self.driver = webdriver.Chrome("./chromedriver", options=options)
        else:
            driver_path, chrome_bin = (
                os.getenv("CHROMEDRIVER_PATH"),
                os.getenv("GOOGLE_CHROME_BIN"),
            )
            options.binary_location = chrome_bin
            self.driver = webdriver.Chrome(executable_path=driver_path, options=options)
        atexit.register(self.close_driver)

    def load_start_page(self):
        self.driver.get(self.homepage)
        return self.driver

    def load_search_page(self):
        start_page = self.load_start_page()
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

    def load_case_records_search_page(self):
        """Clicks into Case Records search page"""

        start_page = self.load_start_page()
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

    def close_driver(self):
        self.driver.close()

    def query_case_id(self, case_id: str):
        # this is the same for travis and williamson.
        search_page = self.load_search_page()
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
            search_soup = BeautifulSoup(search_page_content, "html.parser")
            register_soup = BeautifulSoup(register_page_content, "html.parser")
            return search_soup, register_soup

    def load_court_calendar(self):
        """Opens the court calendar to scrape settings"""

        start_page = self.load_start_page()
        try:
            element = WebDriverWait(start_page, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Court Calendar"))
            )
        finally:
            element.click()
            return start_page
        return None

    def query_settings(
        self, afterdate: datetime.date, beforedate: datetime.date
    ) -> BeautifulSoup:
        """Executes search for case settings between beforedate and afterdate for, returns content of resulting page"""

        for tries in range(5):
            # select Date Range radiobutton for search
            try:
                court_calendar = self.load_court_calendar()
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
            after_box.send_keys(
                afterdate.strftime(format="%m/%d/%Y").lstrip("0").replace("/0", "/")
            )
        except:
            logger.error(f"Could not type in after date {afterdate}")

        # enter after date
        try:
            before_box = WebDriverWait(court_calendar, 10).until(
                EC.presence_of_element_located((By.ID, "DateSettingOnBefore"))
            )
            before_box.clear()
            before_box.send_keys(
                beforedate.strftime(format="%m/%d/%Y").lstrip("0").replace("/0", "/")
            )
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
            return BeautifulSoup(calendar_page_content, "html.parser")

    def query_filings(
        self, afterdate: datetime.date, beforedate: datetime.date, case_num_prefix: str
    ):
        """Executes search for case filings between beforedate and afterdate for case_num_prefix, returns content of resulting page"""

        for tries in range(5):
            # select case in search by
            try:
                court_records = self.load_case_records_search_page()
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
            after_box.send_keys(
                afterdate.strftime(format="%m/%d/%Y").lstrip("0").replace("/0", "/")
            )
        except:
            logger.error(f"Could not type in after date {afterdate}")

        # senter before date
        try:
            before_box = WebDriverWait(court_records, 10).until(
                EC.presence_of_element_located((By.ID, "DateFiledOnBefore"))
            )
            before_box.clear()
            before_box.send_keys(
                beforedate.strftime(format="%m/%d/%Y").lstrip("0").replace("/0", "/")
            )
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

    def fetch_filings(
        self, afterdate: datetime.date, beforedate: datetime.date, case_num_prefix: str
    ) -> List[str]:
        "Get filing case numbers between afterdate and beforedate and starting with case_num_prefix."

        for tries in range(1, 11):
            try:
                filings_page_content = self.query_filings(
                    afterdate, beforedate, case_num_prefix
                )
                filings_soup = BeautifulSoup(filings_page_content, "html.parser")
                (
                    filings_case_nums_list,
                    query_needs_splitting,
                ) = calendars.get_filing_case_nums(filings_soup)
                break
            except:
                if tries == 10:
                    logger.error(f"Failed to find case numbers on all 10 attempts.")
                    query_needs_splitting = False
                    filings_case_nums_list = []

        # handle case of too many results (200 results means that the search cut off)
        if query_needs_splitting:
            try:
                (
                    end_of_first_range,
                    start_of_second_range,
                ) = calendars.split_date_range(afterdate, beforedate)
                filings_case_nums_list = self.fetch_filings(
                    afterdate, end_of_first_range, case_num_prefix
                ) + self.fetch_filings(
                    start_of_second_range, beforedate, case_num_prefix
                )
            except ValueError:
                filings_case_nums_list = None
                logger.error(
                    f"The search returned {len(filings_case_nums_list)} results but there's nothing "
                    "the code can do because beforedate and afterdate are the same.\n"
                    "Case details will be scraped for these results.\n"
                )

        return filings_case_nums_list


class HaysScraper(TravisScraper):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)
        self.homepage = "http://public.co.hays.tx.us/default.aspx"


class WilliamsonScraper(TravisScraper):
    def __init__(self, headless: bool = True) -> None:
        super().__init__(headless=headless)
        self.homepage = "https://judicialrecords.wilco.org/PublicAccess/default.aspx"

    def fetch_parsed_case(self, case_id: str) -> Tuple[str, str]:
        query_result = self.query_case_id(case_id)
        if query_result is None:
            return None
        result_soup, register_soup = query_result

        register_url = case_search.get_register_url(result_soup)
        status, type = case_search.get_status_and_type(result_soup)

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

        parser = hearing.WilliamsonParser()
        return parser.make_parsed_case(
            soup=register_soup, status=status, type=type, register_url=register_url
        )


SCRAPER_NAMES = {
    "test": FakeScraper,
    "travis": TravisScraper,
    "williamson": WilliamsonScraper,
    "wilco": WilliamsonScraper,
}
