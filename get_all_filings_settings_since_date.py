"""Script to get all filings and settings since a given dates. To use: python get_all_filings_since_date.py (m)m-(d)d-yyyy
All dates in this script are in the format (m)m-(d)d-yyyy"""

from datetime import date, datetime, timedelta
import sys
from typing import List, Tuple
import logging

from colorama import Fore, Style
import click
from emailing import send_email
import parse_filings
import parse_settings

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)


def split_into_weeks(start: str, end: str) -> List[Tuple[str, str]]:
    """Returns a list of tuples representing the start and end dates for all weeks between the specified start and end dates"""

    start_date = datetime.strptime(start, "%m-%d-%Y").date()
    end_date = datetime.strptime(end, "%m-%d-%Y").date()

    days_in_range = ((end_date - start_date).days) + 1

    if days_in_range > 7:
        first_end_date = start_date + timedelta(days=6)
        first_end_date_str = first_end_date.strftime("%-m-%-d-%Y")
        next_start_date_str = (first_end_date + timedelta(days=1)).strftime(
            "%-m-%-d-%Y"
        )

        return [(start, first_end_date_str)] + split_into_weeks(
            next_start_date_str, end
        )

    else:
        return [(start, end)]


def try_to_parse(start: str, end: str, tries: int) -> str:
    """
    Parses filings and settings between start and end dates.

    Tries `tries` times before giving up.
    If all attempts fail, returns the start and end date, otherwise returns 'success'.
    """

    for attempt in range(1, tries + 1):
        try:
            parse_filings.parse_filings_on_cloud(start, end, get_old_active=False)
            parse_settings.parse_settings_on_cloud(start, end, write_to_sheets=False)
            logger.info(
                Fore.GREEN
                + f"Successfully parsed filings and settings between {start} and {end} on attempt {attempt}.\n"
                + Style.RESET_ALL
            )

            return "success"
        except Exception as error:
            if attempt == tries:
                logger.error(f"Error message: {error}")

    message = f"{start}, {end}"
    logger.error(
        Fore.RED
        + f"Failed to parse filings and settings between {start} and {end} on all {tries} attempts.\n"
        + Style.RESET_ALL
    )
    return message


def get_all_filings_settings_since_date(start_date: str):
    """Gets all filings and settings since `start_date` but splits it up by week. Logs the weeks that failed."""

    yesterdays_date = (date.today() - timedelta(days=1)).strftime("%-m-%-d-%Y")
    weeks = split_into_weeks(start_date, yesterdays_date)
    logger.info(
        f"Will get all filings and settings between {start_date} and {yesterdays_date}\n"
    )

    failures = []
    for week_start, week_end in weeks:
        msg = try_to_parse(week_start, week_end, 5)
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
            + f"There were no failures when getting all filings between {start_date} and {yesterdays_date} - yay!!"
            + Style.RESET_ALL
        )


if __name__ == "__main__":

    @click.command()
    @click.argument("date", nargs=1)
    def get_all_since_date(date):
        get_all_filings_settings_since_date(date)

    get_all_since_date()
