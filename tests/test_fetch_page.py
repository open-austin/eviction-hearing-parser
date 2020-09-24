import pytest

import fetch_page
import hearing
import parse_filings

class TestFetchFilingsPage:
    def test_fetch_filings_page(self):
        fetched = parse_filings.query_filings(
            afterdate="06/01/2020",
            beforedate="06/10/2020",
            case_num_prefix="J1-CV-20*")
        assert "J1-CV-20-001773" in fetched

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
        parsed = hearing.fetch_parsed_case("J1-CV-20-001590")
        assert (
            parsed["register_url"]
            == "https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2286743"
        )
        assert parsed["status"] == "Final Status"
