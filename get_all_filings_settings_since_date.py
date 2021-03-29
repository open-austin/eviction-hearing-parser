"""
Script to get all filings and settings since a given dates.

To use:
python get_all_filings_since_date.py (m)m-(d)d-yyyy
"""

from datetime import date, timedelta
import sys
from typing import List, Tuple
import logging

import click

import get_all_filings_settings_between_dates as get_filings
import scrapers

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)


def get_all_filings_settings_since_date(start_date: date, county: str):
    """
    Get all filings and settings since `start_date`.

    Splits queries up by week. Logs the weeks that failed.
    """

    yesterdays_date = date.today() - timedelta(days=1)
    get_filings.get_all_filings_settings_between_dates(
        start_date=start_date, end_date=yesterdays_date, county=county
    )


if __name__ == "__main__":

    @click.command()
    @click.argument(
        "date", type=click.DateTime(formats=["%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y"])
    )
    @click.option(
        "--county",
        type=click.Choice(scrapers.SCRAPER_NAMES, case_sensitive=False),
        default="travis",
    )
    def get_all_since_date(date, county):
        get_all_filings_settings_since_date(date, county)

    get_all_since_date()
