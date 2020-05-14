from bs4 import BeautifulSoup
import pytest

import hearing

@pytest.fixture(scope="function")
def soup():
    filepath = hearing.get_test_html_path()
    return hearing.load_soup_from_filepath(filepath)