import pytest

import fetch_page


class TestFetchSearchPage:
    @pytest.mark.skip
    def test_load_start_page(self):
        start_page = fetch_page.load_start_page()
        assert "Select a location" in start_page.page_source
        start_page.close()

    def test_load_search_page(self):
        search_page = fetch_page.load_search_page()
        assert "Selector for the case search type" in search_page.page_source
        search_page.close()
