import logging
import click
import sys
from colorama import Fore, Style
from get_all_filings_settings_since_date import split_into_weeks, try_to_parse
from emailing import send_email

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)


# gets all filings since a given date but splits it up by week, tells you which weeks failed
# date should be string in format (m)m-(d)d-yyyy
def get_all_filings_settings_between_dates(start_date, end_date):
    weeks = split_into_weeks(start_date, end_date)
    logger.info(f"Will get all filings and settings between {start_date} and {end_date}\n")

    failures = []
    for week_start, week_end in weeks:
        msg = try_to_parse(week_start, week_end, 5)
        if msg != "success":
            failures.append(msg)

    if failures:
        failures_str = "\n".join(failures)
        logger.info("All failures:")
        logger.info(Fore.RED + failures_str + Style.RESET_ALL)
        send_email(failures_str, "Date ranges for which parsing filings and settings failed")
    else:
        logger.info(Fore.GREEN + f"There were no failures when getting all filings between {start_date} and {end_date} - yay!!" + Style.RESET_ALL)

if __name__ == "__main__":
    @click.command()
    @click.argument("start_date", nargs=1)
    @click.argument("end_date", nargs=1)


    # dates should be in format (m)m-(d)d-yyyy
    def get_all_between_dates(start_date, end_date):
        get_all_filings_settings_between_dates(start_date, end_date)

    get_all_between_dates()
