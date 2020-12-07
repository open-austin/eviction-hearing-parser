import csv
import os
import click
import hearing
import fetch_page
import persist
import logging
import sys
import simplejson as json
from typing import Any, Dict, List

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)

def get_ids_to_parse(infile: click.File) -> List[str]:
    ids_to_parse = []
    reader = csv.reader(infile)
    for row in reader:
        ids_to_parse.append(row[0])
    return ids_to_parse


def make_case_list(ids_to_parse: List[str]) -> List[Dict[str, Any]]:
    parsed_cases = []
    for id_to_parse in ids_to_parse:
        new_case = hearing.fetch_parsed_case(id_to_parse)
        parsed_cases.append(new_case)
    return parsed_cases

# same as parse_all but takes a list of case_nums rather than a csv
def parse_all_from_parse_filings(case_nums, showbrowser=False):
    if showbrowser:
        from selenium import webdriver
        fetch_page.driver = webdriver.Chrome("./chromedriver")

    parsed_cases = make_case_list(case_nums)
    logger.info(f"Finished making case list, now will all {len(parsed_cases)} cases to SQL.")

    for parsed_case in parsed_cases:
        persist.rest_case(parsed_case)

    logger.info("Finished sending cases to SQL.")

    return parsed_cases

@click.command()
@click.argument(
    "infile", type=click.File(mode="r"),
)
@click.argument("outfile", type=click.File(mode="w"), default="result.json")
@click.option('--showbrowser / --headless', default=False, help='whether to operate in headless mode or not')

def parse_all(infile, outfile, showbrowser=False):
    # If showbrowser is True, use the default selenium driver
    if showbrowser:
        from selenium import webdriver
        fetch_page.driver = webdriver.Chrome("./chromedriver")

    ids_to_parse = get_ids_to_parse(infile)

    for tries in range(5):
        try:
            parsed_cases = make_case_list(ids_to_parse)
            for parsed_case in parsed_cases:
                persist.rest_case(parsed_case)
            json.dump(parsed_cases, outfile)
            logger.info(f"Successfully parsed hearings on attempt {tries + 1}")
            break
        except Exception as e:
            logger.error(f"Failed to parse hearings on attempt {tries + 1}. Error message: {e}")


if __name__ == "__main__":
    parse_all()
