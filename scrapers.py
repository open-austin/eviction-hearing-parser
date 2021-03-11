import logging
import os
from typing import Tuple

from dotenv import load_dotenv

import case_search
from emailing import log_and_email
import hearing
import load_pages

logger = logging.getLogger()


class FakeScraper:
    def query_case_id(self, case_id: str) -> Tuple[str, str]:
        if not case_id == "J1-CV-20-001590":
            raise ValueError(
                "The fake Scraper can only take the Case ID J1-CV-20-001590."
            )
        search_page = load_pages.get_test_search_page(0)
        register_page = load_pages.get_test_soup(0)
        return search_page, register_page

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
