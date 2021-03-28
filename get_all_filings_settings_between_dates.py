"""
Script to get all filings and settings between two dates.

To use:
python get_all_filings_settings_between_dates.py mm-dd-yyy mm-dd-yyyy
"""
from datetime import date, timedelta
import logging
import sys
from typing import List, Tuple

import click
from colorama import Fore, Style

from emailing import send_email
import parse_filings
import parse_settings
import scrapers

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)


def split_into_weeks(start: date, end: date) -> List[Tuple[date, date]]:
    """Get start and end dates for all weeks between specified start and end dates."""

    days_in_range = ((end - start).days) + 1

    if days_in_range > 7:
        first_end_date = start + timedelta(days=6)
        next_start_date = first_end_date + timedelta(days=1)

        return [(start, first_end_date)] + split_into_weeks(next_start_date, end)

    else:
        return [(start, end)]


def try_to_parse(
    start: str, end: str, tries: int, scraper: scrapers.TestScraper
) -> str:
    """
    Parses filings and settings between start and end dates.

    Tries `tries` times before giving up.
    If all attempts fail, returns the start and end date, otherwise returns 'success'.
    """

    for attempt in range(1, tries + 1):
        try:
            parse_filings.parse_filings_on_cloud(
                afterdate=start, beforedate=end, get_old_active=False, scraper=scraper
            )
            parse_settings.parse_settings_on_cloud(
                afterdate=start, beforedate=end, write_to_sheets=False, scraper=scraper
            )
            logger.info(
                Fore.GREEN
                + "Successfully parsed filings and settings "
                + f"between {start} and {end} on attempt {attempt}.\n"
                + Style.RESET_ALL
            )

            return "success"
        except Exception as error:
            if attempt == tries:
                logger.error(f"Error message: {error}")

    message = f"{start}, {end}"
    logger.error(
        Fore.RED
        + f"Failed to parse filings and settings between {start} "
        + f"and {end} on all {tries} attempts.\n"
        + Style.RESET_ALL
    )
    return message


def get_all_filings_settings_between_dates(
    start_date: date, end_date: date, county: str, showbrowser=bool
):
    """
    Gets all filings and settings between `start_date` and `end_date` but splits it up by week.

    Logs the weeks that failed.
    """

    weeks = split_into_weeks(start_date, end_date)
    logger.info(
        f"Will get all filings and settings between {start_date} and {end_date}\n"
    )

    failures = []
    scraper = scrapers.SCRAPER_NAMES[county](headless=not showbrowser)
    for week_start, week_end in weeks:
        msg = try_to_parse(week_start, week_end, 5, scraper=scraper)
        if msg != "success":
            failures.append(msg)

    if failures:
        failures_str = "\n".join(failures)
        logger.info("All failures:")
        logger.info(Fore.RED + failures_str + Style.RESET_ALL)
        send_email(
            failures_str, "Date ranges for which parsing filings and settings failed"
        )
    else:
        logger.info(
            Fore.GREEN
            + "There were no failures when getting all filings "
            + f"between {start_date} and {end_date} - yay!!"
            + Style.RESET_ALL
        )


if __name__ == "__main__":

    @click.command()
    @click.argument(
        "start_date", type=click.DateTime(formats=["%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y"])
    )
    @click.argument(
        "end_date", type=click.DateTime(formats=["%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y"])
    )
    @click.option(
        "--county",
        type=click.Choice(scrapers.SCRAPER_NAMES, case_sensitive=False),
        default="travis",
    )

    # dates should be in format (m)m-(d)d-yyyy
    def get_all_between_dates(start_date, end_date, county):
        get_all_filings_settings_between_dates(start_date, end_date, county)

    get_all_between_dates()
