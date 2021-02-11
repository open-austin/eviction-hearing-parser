import pytest

import fetch_page
import hearing


class TestFetchFilingsPage:
    def test_fetch_filings_page(self):
        fetched = fetch_page.query_filings(
            afterdate="6-1-2020", beforedate="6-30-2020", case_num_prefix="J1-CV-20*"
        )
        assert "J1-CV-20-001773" in fetched


class TestFetchCaseNumbers:
    def test_fetch_case_numbers_requiring_split(self):
        """
        Test date range requiring multiple pages of search results.

        The scraper will need to split this into multiple queries and combine the results.
        """
        numbers = fetch_page.fetch_filings(
            afterdate="1-1-2020", beforedate="1-30-2020", case_num_prefix="J1-CV-20*"
        )
        assert "J1-CV-20-000001" in numbers
        assert len(numbers) > 200


class TestFetchSearchPage:
    def test_load_start_page(self):
        start_page = fetch_page.load_start_page()
        assert "Select a location" in start_page.page_source

    def test_load_search_page(self):
        search_page = fetch_page.load_search_page()
        assert "Selector for the case search type" in search_page.page_source

    def test_query_case_id(self):
        search_page_content, register_page_content = fetch_page.query_case_id(
            "J1-CV-20-001590"
        )
        assert "04/27/2020" in register_page_content


class TestDataFromScrapedPage:
    def test_url_for_register(self):
        parsed = fetch_page.fetch_parsed_case("J1-CV-20-001590")
        assert (
            parsed["register_url"]
            == "https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2286743"
        )
        assert parsed["status"] == "Final Status"
