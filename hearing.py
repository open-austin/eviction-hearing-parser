import os

from bs4 import BeautifulSoup

def get_test_html_path():
    this_directory = os.path.dirname(os.path.realpath(__file__))
    test_directory = os.path.join(this_directory, "tests", "example_register.html")
    return test_directory

def load_soup_from_filepath(filepath: str):
    with open(filepath) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    return soup

def get_plaintiff(soup):
    tag = soup.find(text="Defendant").parent
    defendant_name_tag = tag.find_next_sibling("th")

    return defendant_name_tag.text