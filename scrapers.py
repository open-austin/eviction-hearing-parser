import logging
import os
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv

import case_search
from emailing import log_and_email
import hearing
import load_pages

logger = logging.getLogger()


class BaseScraper:
    pass


class FakeScraper(BaseScraper):
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

    def make_case_list(
        self, ids_to_parse: List[str], showbrowser: bool = False
    ) -> List[Dict[str, Any]]:
        """Gets case details for each case number in `ids_to_pars`"""

        parsed_cases, failed_ids = [], []
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
