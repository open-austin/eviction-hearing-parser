import os

from bs4 import BeautifulSoup


def get_test_html_path(index: int) -> str:
    this_directory = os.path.dirname(os.path.realpath(__file__))
    test_filepath = os.path.join(this_directory, "test_pages", f"example_{index}.html")
    return test_filepath


def load_soup_from_filepath(filepath: str) -> BeautifulSoup:
    with open(filepath) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    return soup


def get_test_soup(index: int) -> BeautifulSoup:
    filepath = get_test_html_path(index)
    return load_soup_from_filepath(filepath)


def get_plaintiff(soup):
    tag = soup.find(text="Plaintiff").parent
    name_elem = tag.find_next_sibling("th")

    return name_elem.text
