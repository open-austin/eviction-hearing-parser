"""
Module to get data for all cases between two dates
To perform a scraper run, use: python parse_filings.py afterdate beforedate
(dates in format mm-dd-yyyy)
"""
import datetime
import os
import sys
import json
from typing import List, Dict, Optional

import click
import scrapers
from parse_hearings import parse_all_from_parse_filings, persist_parsed_cases

import logging

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)


def parse_filings_on_cloud(
    afterdate: datetime.date,
    beforedate: datetime.date,
    get_old_active=True,
    showbrowser=False,
    scraper: Optional[scrapers.TestScraper] = None,
):
    """Parses filings without command line interface and outfile options."""

    logger.info(f"Parsing filings between {afterdate} and {beforedate}.")

    if not scraper:
        scraper = scrapers.TravisScraper(headless=not showbrowser)

    all_case_nums = scraper.get_all_case_nums(
        afterdate=afterdate, beforedate=beforedate
    )
    if get_old_active:
        from persist import get_old_active_case_nums

        all_case_nums += get_old_active_case_nums()

    # using dict to eliminate duplicates
    all_case_nums = list(dict.fromkeys(all_case_nums))
    logger.info(f"Found {len(all_case_nums)} case numbers (including old active ones).")
    cases = parse_all_from_parse_filings(all_case_nums, scraper=scraper)

    # persist cases only if not using the test scraper
    if isinstance(scraper, scrapers.TravisScraper):
        persist_parsed_cases(cases)

    return cases


@click.command()
@click.argument(
    "afterdate",
    type=click.DateTime(formats=["%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y"]),
    nargs=1,
)
@click.argument(
    "beforedate",
    type=click.DateTime(formats=["%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y"]),
    nargs=1,
)
@click.argument("outfile", type=click.File(mode="w"), required=False)
@click.option(
    "--showbrowser / --headless",
    default=False,
    help="whether to operate in headless mode or not",
)
def parse_filings(
    afterdate: datetime.date, beforedate: datetime.date, outfile, showbrowser=False
):
    """
    Perform a full 'scraper run' between `afterdate` and `beforedate`.

    Gets case details, events, and dispositions for all case numbers between
    `afterdate` and `beforedate`.
    Example of date format: 9-1-2020.
    Also updates rows in event/disposition/case_detail table that are still active.
    """
    parsed_cases = parse_filings_on_cloud(
        afterdate=afterdate, beforedate=beforedate, showbrowser=showbrowser
    )

    if outfile:
        json.dump(parsed_cases, outfile)
    return parsed_cases


if __name__ == "__main__":
    parse_filings()
