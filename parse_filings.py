"""
Module to get data for all cases between two dates
To perform a scraper run, use: python parse_filings.py afterdate beforedate
(dates in format mm-dd-yyyy)
"""

import os
import sys
import json
from typing import List, Dict

import click
import fetch_page
from fetch_page import fetch_filings
from parse_hearings import parse_all_from_parse_filings
from persist import get_old_active_case_nums
from selenium import webdriver
import logging

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)

def get_all_case_nums(afterdate: str, beforedate: str) -> List[str]:
    """Gets list of all case numbers between `afterdate` and `beforedate` (dates are in format mm-dd-yyyy)"""

    aferdate_year = afterdate.split("-")[-1][-2:]
    beforedate_year = beforedate.split("-")[-1][-2:]

    years = set([aferdate_year, beforedate_year])
    case_num_prefixes = []
    for year in years:
        case_num_prefixes += [f"J1-CV-{year}*", f"J2-CV-{year}*", f"J3-EV-{year}*", f"J4-CV-{year}*", f"J5-CV-{year}*"]

    all_case_nums = []
    for prefix in case_num_prefixes:
        prefix_case_nums = fetch_filings(afterdate, beforedate, prefix)
        all_case_nums += prefix_case_nums

    logger.info(f"Scraped case numbers between {afterdate} and {beforedate} - found {len(all_case_nums)} of them.")
    return all_case_nums

def parse_filings_on_cloud(afterdate: str, beforedate: str, get_old_active=True):
    """Same as `parse_filings()` (see below) but without command line interface and showbrowser/outfile options"""

    logger.info(f"Parsing filings between {afterdate} and {beforedate}.")

    if get_old_active:
        all_case_nums = get_all_case_nums(afterdate, beforedate) + get_old_active_case_nums()
    else:
        all_case_nums = get_all_case_nums(afterdate, beforedate)

    logger.info(f"Found {len(all_case_nums)} case numbers (including old active ones).")
    parse_all_from_parse_filings(all_case_nums)

@click.command()
@click.argument("afterdate", nargs=1)
@click.argument("beforedate", nargs=1)
@click.argument("outfile", type=click.File(mode="w"), default="result.json")
@click.option('--showbrowser / --headless', default=False, help='whether to operate in headless mode or not')


def parse_filings(afterdate, beforedate, outfile, showbrowser=False):
    """
    Performs a full 'scraper run' between `afterdate` and `beforedate` - gets case details, events, and dispositions for all case numbers between
    `afterdate` and `beforedate`. Example of date format: 9-1-2020. Also updates rows in event/disposition/case_detail table that are still active
    """

    # use default chrome browser (rather than headless) is showbrowser is True
    if showbrowser:
        fetch_page.driver = webdriver.Chrome("./chromedriver")

    all_case_nums = get_all_case_nums(afterdate, beforedate) + get_old_active_case_nums()
    parsed_cases = parse_all_from_parse_filings(all_case_nums, showbrowser=showbrowser)

    try:
        json.dump(parsed_cases, outfile)
    except:
        logger.error("Creating the json file may have been unsuccessful.")

if __name__ == "__main__":
    parse_filings()
