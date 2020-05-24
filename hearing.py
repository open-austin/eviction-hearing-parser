import os
from typing import Dict

from bs4 import BeautifulSoup


def get_test_html_path(index: int, page_type: str) -> str:
    this_directory = os.path.dirname(os.path.realpath(__file__))
    test_filepath = os.path.join(this_directory, page_type, f"example_{index}.html")
    return test_filepath


def load_soup_from_filepath(filepath: str) -> BeautifulSoup:
    with open(filepath) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    return soup


def get_test_soup(index: int) -> BeautifulSoup:
    filepath = get_test_html_path(index, page_type="test_pages")
    return load_soup_from_filepath(filepath)


def get_test_search_page(index: int) -> BeautifulSoup:
    filepath = get_test_html_path(index, page_type="test_search_pages")
    return load_soup_from_filepath(filepath)


def get_plaintiff(soup):
    tag = soup.find(text="Plaintiff").parent
    name_elem = tag.find_next_sibling("th")

    return name_elem.text


def get_defendants(soup):
    defendants = []
    for tag in soup.find_all(text="Defendant"):
        name_elem = tag.parent.find_next_sibling("th")
        defendants.append(name_elem.text)
    together = "; ".join(defendants)
    return together


def get_case_number(soup):
    elem = soup.find(class_="ssCaseDetailCaseNbr").span
    return elem.text


def get_style(soup):
    elem = soup.find_all("table")[4].tbody.tr.td
    return elem.text


def get_zip(soup):
    def has_austin(string: str) -> bool:
        return "austin, tx" in string.lower()

    zip_tag = soup.find(string=has_austin)
    zipcode = zip_tag.strip().split()[-1]
    return zipcode


def get_hearing_tag(soup):
    def ends_with_hearing(string: str) -> bool:
        return string.endswith("Hearing")

    return soup.find_all("b", string=ends_with_hearing)[-1]


def get_hearing_text(soup):
    hearing_tag = get_hearing_tag(soup)
    return hearing_tag.next_sibling


def get_hearing_date(soup):
    hearing_tag = get_hearing_tag(soup)
    date_tag = hearing_tag.parent.find_previous_sibling("th")
    return date_tag.text


def get_hearing_time(soup):
    hearing_text = get_hearing_text(soup)
    up_to_time = hearing_text.split(")")[0]
    just_time = up_to_time.split("(")[1]
    return just_time


def get_hearing_officer(soup):
    hearing_text = get_hearing_text(soup)
    name = hearing_text.split("Judicial Officer")[1]
    return name.strip().strip(")")


def get_precinct_number(soup):
    word_to_number = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    location_heading = soup.find(text="Location:").parent
    precinct_name = location_heading.find_next_sibling("td").text
    precinct_number = precinct_name.split("Precinct ")[1]

    return word_to_number[precinct_number]


def get_status(status_soup):
    eviction_tag = status_soup.find(text="Eviction")
    status_tag = eviction_tag.parent.find_next_sibling("div")
    return status_tag.text


def make_parsed_hearing(soup) -> Dict[str, str]:
    return {
        "precinct_number": get_precinct_number(soup),
        "style": get_style(soup),
        "plaintiff": get_plaintiff(soup),
        "defendants": get_defendants(soup),
        "case_number": get_case_number(soup),
        "zip": get_zip(soup),
        "hearing_date": get_hearing_date(soup),
        "hearing_time": get_hearing_time(soup),
        "hearing_officer": get_hearing_officer(soup),
    }
