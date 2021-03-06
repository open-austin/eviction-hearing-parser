from datetime import date

import pytest

import scrapers
import config

config.county = "travis"

scraper = scrapers.TravisScraper()
williamson_scraper = scrapers.WilliamsonScraper()


class TestFetchFilingsPage:
    def test_fetch_filings_page(self):

        fetched = scraper.query_filings(
            afterdate=date(2020, 6, 1),
            beforedate=date(2020, 6, 30),
            case_num_prefix="J1-CV-20*",
        )
        assert "J1-CV-20-001773" in fetched


class TestFetchCaseNumbers:
    def test_fetch_case_numbers_requiring_split(self):
        """
        Test date range requiring multiple pages of search results.

        The scraper will need to split this into multiple queries and combine the results.
        """
        numbers = scraper.fetch_filings(
            afterdate=date(2020, 1, 1),
            beforedate=date(2020, 1, 30),
            case_num_prefix="J1-CV-20*",
        )
        assert "J1-CV-20-000001" in numbers
        assert len(numbers) > 200


class TestFetchSearchPage:
    # travis county tests
    def test_load_start_page(self):
        start_page = scraper.load_start_page()
        assert "Select a location" in start_page.page_source

    def test_load_search_page(self):
        search_page = scraper.load_search_page()
        assert "Selector for the case search type" in search_page.page_source

    def test_query_case_id(self):
        search_page_content, register_page_content = scraper.query_case_id(
            "J1-CV-20-001590"
        )
        assert "04/27/2020" in register_page_content

    # williamson county tests
    def test_load_start_page(self):
        # set county for this batch of tests
        print(config.county)

        start_page = williamson_scraper.load_start_page()
        assert "Select a location" in start_page.page_source

    def test_load_search_page(self):
        search_page = williamson_scraper.load_search_page()
        assert "Selector for the case search type" in search_page.page_source

    def test_query_case_id(self):
        search_page_content, register_page_content = williamson_scraper.query_case_id(
            "1JC-21-0116"
        )
        assert "02/02/2021" in str(register_page_content)


class TestDataFromScrapedPage:
    def test_url_for_register(self):

        parsed = scraper.fetch_parsed_case("J1-CV-20-001590")
        assert (
            parsed.register_url
            == "https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx?CaseID=2286743"
        )
        assert parsed.status == "Final Status"
