from datetime import date, datetime, timedelta
from schedule import send_email
from parse_filings import parse_filings_on_cloud
from colorama import Fore, Style


# dates should be strings in format m/d/yyyy
def split_into_weeks(start, end):
    start_date = datetime.strptime(start, "%m/%d/%Y").date()
    end_date = datetime.strptime(end, "%m/%d/%Y").date()

    days_in_range = ((end_date - start_date).days) + 1

    if days_in_range > 7:
        first_end_date = start_date + timedelta(days=6)
        first_end_date_str = first_end_date.strftime("%-m/%-d/%Y")
        next_start_date_str = (first_end_date + timedelta(days=1)).strftime("%-m/%-d/%Y")

        return [(start, first_end_date_str)] + split_into_weeks(next_start_date_str, end)

    else:
        return [(start, end)]


# stat, end are dates as strings
def try_to_parse(start, end, tries):
    for attempt in range(1, tries + 1):
        try:
            parse_filings_on_cloud(start, end)
            print(Fore.GREEN + f"Successfully parsed filings (happy) between {start} and {end} on {attempt}th attempt.\n" + Style.RESET_ALL)
            return "success"
        except Exception as error:
            if attempt == tries:
                print("Error message:", error)

    message = f"{start}, {end}"
    print(Fore.RED + f"Failed to parse filings (sadly) between {start} and {end}.\n" + Style.RESET_ALL)
    return message


# when doing this, should remove the get_old_active_case_nums from parse_filings_on_cloud function
# date should be string in format mm/dd/yyyy
def get_all_filings_since_date(start_date):
    yesterdays_date = (date.today() - timedelta(days=1)).strftime("%-m/%-d/%Y")
    weeks = split_into_weeks(start_date, yesterdays_date)
    print(f"Will get all filings between {start_date} and {yesterdays_date}\n")

    failures = []
    for week_start, week_end in weeks:
        msg = try_to_parse(week_start, week_end, 5)
        if msg != "success":
            failures.append(msg)

    if failures:
        failures_str = "\n".join(failures)
        print("All failures:")
        print(Fore.RED + failures_str + Style.RESET_ALL)
        send_email(failures_str, "Date ranges for which parsing files failed")
    else:
        print(Fore.GREEN + f"There were no failures when getting all filings between {start_date} and {yesterdays_date} - yay!!" + Style.RESET_ALL)


get_all_filings_since_date("10/12/2020")
