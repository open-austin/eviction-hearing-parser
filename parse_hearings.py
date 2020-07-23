import csv
import simplejson as json
import os
from typing import Any, Dict, List

import click
import hearing
import fetch_page
import persist


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
        fetch_page.driver = webdriver.Firefox()

    ids_to_parse = get_ids_to_parse(infile)
    parsed_cases = make_case_list(ids_to_parse)
    for parsed_case in parsed_cases:
        persist.rest_case(parsed_case)
    json.dump(parsed_cases, outfile)


if __name__ == "__main__":
    parse_all()
