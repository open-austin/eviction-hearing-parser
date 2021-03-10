import os

from bs4 import BeautifulSoup


def get_test_html_path(index: int, page_type: str, county: str = "example") -> str:
    this_directory = os.path.dirname(os.path.realpath(__file__))
    test_filepath = os.path.join(this_directory, page_type, f"{county}_{index}.html")
    return test_filepath


def get_test_calendar_path() -> str:
    this_directory = os.path.dirname(os.path.realpath(__file__))
    test_filepath = os.path.join(this_directory, "test_search_pages", "calendar.html")
    return test_filepath


def get_test_filing_search_path() -> str:
    """Used for testing the separate module "parse_filings.py"."""
    this_directory = os.path.dirname(os.path.realpath(__file__))
    test_filepath = os.path.join(
        this_directory, "test_search_pages", f"example_case_query_result.html"
    )
    return test_filepath


def load_soup_from_filepath(filepath: str) -> BeautifulSoup:
    with open(filepath) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    return soup


def get_test_calendar() -> BeautifulSoup:
    filepath = get_test_calendar_path()
    return load_soup_from_filepath(filepath)


def get_test_soup(index: int) -> BeautifulSoup:
    filepath = get_test_html_path(index, page_type="test_pages")
    return load_soup_from_filepath(filepath)


def get_test_williamson(index: int) -> BeautifulSoup:
    filepath = get_test_html_path(index, page_type="test_pages", county="williamson")
    return load_soup_from_filepath(filepath)


def get_test_search_page(index: int) -> BeautifulSoup:
    filepath = get_test_html_path(index, page_type="test_search_pages")
    return load_soup_from_filepath(filepath)


def get_test_filings_search_page() -> BeautifulSoup:
    """
    Used for testing the separate module "parse_filings.py".

    This may or may not need to be distinct from get_test_search_page above.
    Possibly the functions being tested can be consolidated.
    """
    filepath = get_test_filing_search_path()
    return load_soup_from_filepath(filepath)


def get_test_calendar_page() -> BeautifulSoup:
    filepath = get_test_calendar_path()
    return load_soup_from_filepath(filepath)
