from datetime import date, datetime, timedelta
import sys
import logging
from colorama import Fore, Style
import click
from emailing import send_email
import gsheet
import parse_filings
import parse_settings

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)
# dates should be strings in format (m)m-(d)d-yyyy
def split_into_weeks(start, end):
    start_date = datetime.strptime(start, "%m-%d-%Y").date()
    end_date = datetime.strptime(end, "%m-%d-%Y").date()

    days_in_range = ((end_date - start_date).days) + 1

    if days_in_range > 7:
        first_end_date = start_date + timedelta(days=6)
        first_end_date_str = first_end_date.strftime("%-m-%-d-%Y")
        next_start_date_str = (first_end_date + timedelta(days=1)).strftime("%-m-%-d-%Y")

        return [(start, first_end_date_str)] + split_into_weeks(next_start_date_str, end)

    else:
        return [(start, end)]

# start, end are dates as strings
def try_to_parse(start, end, tries):
    for attempt in range(1, tries + 1):
        try:
            parse_filings.parse_filings_on_cloud(start, end, get_old_active=False)
            parse_settings.parse_settings_on_cloud(start, end, write_to_sheets=False)
            logger.info(Fore.GREEN + f"Successfully parsed filings and settings between {start} and {end} on attempt {attempt}.\n" + Style.RESET_ALL)

            return "success"
        except Exception as error:
            if attempt == tries:
                logger.error(f"Error message: {error}")

    message = f"{start}, {end}"
    logger.error(Fore.RED + f"Failed to parse filings and settings between {start} and {end} on all {tries} attempts.\n" + Style.RESET_ALL)
    return message

# gets all filings since a given date but splits it up by week, tells you which weeks failed
# date should be string in format (m)m-(d)d-yyyy
def get_all_filings_settings_since_date(start_date):
    yesterdays_date = (date.today() - timedelta(days=1)).strftime("%-m-%-d-%Y")
    weeks = split_into_weeks(start_date, yesterdays_date)
    logger.info(f"Will get all filings and settings between {start_date} and {yesterdays_date}\n")

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
        logger.info(Fore.GREEN + f"There were no failures when getting all filings between {start_date} and {yesterdays_date} - yay!!" + Style.RESET_ALL)

if __name__ == "__main__":
    @click.command()
    @click.argument("date", nargs=1)

    # date should be in format (m)m-(d)d-yyyy
    def get_all_since_date(date):
        get_all_filings_settings_since_date(date)

    get_all_since_date()
    #dump to sheets
    gsheet.dump_to_sheets('Court_scraper_filings_archive','filings_archive',"SELECT "+ cols + " FROM filings_archive")
    gsheet.dump_to_sheets('Court_scraper_filings_archive','events',"SELECT * FROM event")
    gsheet.dump_to_sheets('Court_scraper_settings_archive','settings_archive',"SELECT * FROM setting")
    gsheet.dump_to_sheets('Court_scraper_evictions_archive','evictions_archive',"SELECT "+ cols +" FROM filings_archive WHERE case_type='Eviction'") #Convert Date to Text
    gsheet.dump_to_sheets('Court_scraper_evictions_archive','events',"SELECT * FROM eviction_events")

