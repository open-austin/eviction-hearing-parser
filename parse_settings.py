"""
Module to get setting details between two dates.
To perform a scraper run, use: python parse_settings.py afterdate beforedate
(dates in format (m)m-(d)d-yyyy)
"""
import datetime as dt
import logging
import sys
from typing import Any, Dict, List, Optional

import click
import simplejson as json

import scrapers

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)


def get_days_between_dates(afterdate: str, beforedate: str):
    "Return a list of individual days between two dates"

    # get days between as int
    n_days = (beforedate - afterdate).days

    # return each individual day, including the last one
    return [(afterdate + dt.timedelta(days=i)) for i in range(n_days + 1)]


def make_setting_list(days_to_pull: List[str]) -> List[Dict[str, Any]]:
    """Pulls all settings, one day at a time"""
    scraper = scrapers.TravisScraper()
    pulled_settings = []
    for setting_day in days_to_pull:
        day_settings = scraper.fetch_settings(
            afterdate=setting_day, beforedate=setting_day
        )
        pulled_settings.extend(day_settings)
    return pulled_settings


def parse_settings_on_cloud(afterdate: str, beforedate: str, write_to_sheets=True):
    """
    Same as `parse_settings()` (see below) but without command line interface and showbrowser option.
    Outputs scraped results to a gsheet:Settings_scheduler if `write_to_sheets` is True
    """

    logger.info(f"Parsing settings between {afterdate} and {beforedate}.")

    days_to_pull = get_days_between_dates(afterdate=afterdate, beforedate=beforedate)
    pulled_settings = make_setting_list(days_to_pull)
    import persist

    for setting in pulled_settings:
        persist.rest_setting(setting)
    # maybe make this cleaner in sql? future work
    if write_to_sheets:
        import gsheet

        gsheet.write_pulled_settings(pulled_settings)


def parse_settings(afterdate: str, beforedate: str, outfile: str, showbrowser=False):
    """Gets data for all settings between `afterdate` and `beforedate` and sends results to PostgreSQL database."""

    # If showbrowser is True, use the default selenium driver
    if showbrowser:
        from selenium import webdriver

        fetch_page.driver = webdriver.Chrome("./chromedriver")

    days_to_pull = get_days_between_dates(afterdate=afterdate, beforedate=beforedate)
    pulled_settings = make_setting_list(days_to_pull)
    return pulled_settings


def _parse_and_persist_settings(
    afterdate: dt.date,
    beforedate: dt.date,
    outfile: str = "",
    showbrowser: bool = False,
    db: bool = True,
    gs: bool = True,
):
    pulled_settings = parse_settings(afterdate, beforedate, outfile, showbrowser)
    if db:
        import persist

        for setting in pulled_settings:
            persist.rest_setting(setting)
    if gs:
        import gsheet

        gsheet.write_pulled_settings(pulled_settings)

    if outfile:
        json.dump(pulled_settings, outfile)
    return pulled_settings


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
@click.option("--outfile", type=click.File(mode="w"), required=False)
@click.option(
    "--showbrowser / --headless",
    default=False,
    help="whether to operate in headless mode or not",
)
@click.option(
    "--db / --no-db",
    default=True,
    help="whether to persist data to database",
)
@click.option(
    "--gs / --no-gs",
    default=True,
    help="whether to persist data to Google Sheets",
)
def parse_and_persist_settings(
    afterdate: dt.date,
    beforedate: dt.date,
    outfile: str = "",
    showbrowser: bool = False,
    db: bool = True,
    gs: bool = True,
):
    """Pass same values to an alias function that isn't a Click command."""
    return _parse_and_persist_settings(
        afterdate=afterdate,
        beforedate=beforedate,
        outfile=outfile,
        showbrowser=showbrowser,
        db=db,
        gs=gs,
    )


if __name__ == "__main__":
    parse_and_persist_settings()
