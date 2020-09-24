import csv
import os
import click
import logging
import sqlite3
import atexit
import parse_hearings
from datetime import date, datetime
from datetime import timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
logger = logging.getLogger()
options = Options()
options.add_argument("--headless")
options.add_argument('window-size=1920,1080')

driver = webdriver.Firefox(options=options)
def close_driver():
    driver.close()
atexit.register(close_driver)

# loads official records home page
def load_start_page():
    driver.get("https://odysseypa.traviscountytx.gov/JPPublicAccess/default.aspx")
    return driver

# clicks into case records page
def load_case_records():
    start_page = load_start_page()
    try:
        element = WebDriverWait(start_page, 10).until(
            EC.presence_of_element_located(
                (By.LINK_TEXT, "Civil, Family & Probate Case Records")
            )
        )
    finally:
        element.click()
        return start_page
    return None

# executes search for case filings between beforedate and afterdate for case_num_prefix, returns content of resulting page
def query_filings(afterdate: str, beforedate: str, case_num_prefix: str):
    for tries in range(5):
        # select case in search by
        try:
            court_records = load_case_records()
            case_button = WebDriverWait(court_records, 10).until(
                EC.presence_of_element_located((By.ID, "Case"))
            )
            case_button.click()
            break
        except Exception as e:
            logger.error(f"Could not click button to search filings by Case, try {tries}")

    # enter after date
    try:
        after_box = WebDriverWait(court_records, 10).until(
            EC.presence_of_element_located((By.ID, "DateFiledOnAfter"))
        )
        after_box.clear()
        after_box.send_keys(afterdate)
    except:
        logger.error(f"Could not type in after date {afterdate}")

    #senter before date
    try:
        before_box = WebDriverWait(court_records, 10).until(
            EC.presence_of_element_located((By.ID, "DateFiledOnBefore"))
        )
        before_box.clear()
        before_box.send_keys(beforedate)
    except Exception as e:
        logger.error(f"Could not type in before date {beforedate}")

    # type in case number prefix
    try:
        before_box = WebDriverWait(court_records, 10).until(
            EC.presence_of_element_located((By.ID, "CaseSearchValue"))
        )
        before_box.clear()
        before_box.send_keys(case_num_prefix)
    except:
        logger.error(f"Could not type in case number prefix {case_num_prefix}")

    #click search button
    try:
        settings_link = WebDriverWait(court_records, 10).until(
            EC.presence_of_element_located((By.ID, "SearchSubmit"))
        )
        settings_link.click()
    except:
        logger.error(f"Could not click search button for dates {afterdate} {beforedate}, prefix {case_num_prefix}")

    finally:
        records_page_content = court_records.page_source
        return records_page_content

# returns list of case numbers given soup of search results
def get_filing_case_nums(filing_soup):

    #get all tables
    table_list = filing_soup.find_all("table")

    #get first table containing string "Filed/Location" in a header (get the main table of the page)
    filings_table = [table for table in table_list if table.find("th", text="Filed/Location") is not None][0]

    #get the header row, and all next siblings as a list
    header_row = filings_table.find_all('tr')[0]
    tablerow_list = header_row.find_next_siblings('tr')
    if len(tablerow_list) == 0:
        return []

    #go row by row, get case number
    case_nums = []
    for tablerow in tablerow_list:
        td_list = tablerow.find_all('td')
        try:
            if "Eviction" in td_list[3].text:
                case_num = td_list[0].text
                if case_num is not None:
                    case_nums.append(case_num)
        except:
            logger.error(f"Couldn't get case number for row {table_row}")

    # handle case of no results
    if (len(case_nums) == 1) and ("No cases matched" in case_nums[0]):
        case_nums = []

    return case_nums

# splits date range in half - requires inputs in format "m/d/y" - returns 4 strings representing two new date ranges
def split_date_range(afterdate, beforedate):
    # this should never happen the way fetch_filings is defined
    if afterdate == beforedate:
        logger.error("split_date_range function was called with the same beforedate and afterdate.")
        return

    afterdate_parts, beforedate_parts = afterdate.split("/"), beforedate.split("/")
    afterdate_date = date(month=int(afterdate_parts[0]), day=int(afterdate_parts[1]), year=int(afterdate_parts[2]))
    beoforedate_date = date(month=int(beforedate_parts[0]), day=int(beforedate_parts[1]), year=int(beforedate_parts[2]))

    time_between_dates = beoforedate_date - afterdate_date
    days_to_add = (time_between_dates / 2).days

    new_beforedate_date = afterdate_date + timedelta(days=days_to_add)
    new_afterdate_date = new_beforedate_date + timedelta(days=1)

    new_beforedate = new_beforedate_date.strftime("%-m/%-d/%Y")
    new_afterdate = new_afterdate_date.strftime("%-m/%-d/%Y")

    return afterdate, new_beforedate, new_afterdate, beforedate

# returns list of filing case numbers between afterdate and beforedate and starting with case_num_prefix
def fetch_filings(afterdate: str, beforedate: str, case_num_prefix: str):
    # try 5 times
    for try_num in range(5):
        try:
            print(f"Scraping case numbers between {afterdate} and {beforedate} for prefix {case_num_prefix}...")
            filings_page_content = query_filings(afterdate, beforedate, case_num_prefix)
            filings_soup = BeautifulSoup(filings_page_content, "html.parser")
            filings_case_nums_list = get_filing_case_nums(filings_soup)

            # handle case of too many results (200 results means that the search cut off)
            num_results = len(filings_case_nums_list)
            if num_results >= 200:
                # should be very rare
                if afterdate == beforedate:
                    logger.error(f"The search returned {num_results} results but there's nothing the code can do because beforedate and afterdate are the same.\nCase details will be scraped for these 200 results.\n")
                else:
                    print(f"Got a result bigger than 200 ({num_results}), splitting date range.\n")
                    afterdate1, beforedate1, afterdate2, beforedate2 = split_date_range(afterdate, beforedate)
                    return fetch_filings(afterdate1, beforedate1, case_num_prefix) + fetch_filings(afterdate2, beforedate2, case_num_prefix)

            # some logging to make sure results look good - could remove
            print(f"Found {num_results} case numbers.")
            if num_results > 5:
                print(f"Results preview: {filings_case_nums_list[0]}, {filings_case_nums_list[1]}, ..., {filings_case_nums_list[num_results - 1]}\n")
            else:
                print(f"Results: {', '.join(filings_case_nums_list)}\n")

            return filings_case_nums_list

        except:
            logger.error(f"Try {try_num + 1} out of 5 failed.\n")

# returns list of all case nums for all prefixes between afterdate and beforedate
def get_all_case_nums(afterdate: str, beforedate: str):
    case_num_prefixes = ["J1-CV-20*", "J2-CV-20*", "J3-EV-20*", "J4-CV-20*", "J5-CV-20*"]
    all_case_nums = []
    for prefix in case_num_prefixes:
        prefix_case_nums = fetch_filings(afterdate, beforedate, prefix)
        all_case_nums += prefix_case_nums
    return all_case_nums

# drops all rows with case number in case_ids from table table_name - meant to be used for case_detail, disposition, and event tables only (won't work for settings)
def drop_rows_from_table(table_name: str, case_ids: list):
    if len(case_ids) == 1:
        case_ids = str(tuple(case_ids)).replace(",", "")
    else:
        case_ids = str(tuple(case_ids))

    conn = sqlite3.connect("cases.db")
    curs = conn.cursor()

    if table_name == "CASE_DETAIL":
        query_string = 'delete from "' + table_name + '" where "ID" in ' + case_ids
        curs.execute(query_string)
    else:
        query_string = 'delete from "' + table_name + '" where "CASE_DETAIL_ID" in ' + case_ids
        curs.execute(query_string)

    conn.commit()
    curs.close()

# returns list of case nums in sqlite that are still active, removes all rows with those case numbers from case_detail, disposition, and event tables
def get_old_active_case_nums():
    conn = sqlite3.connect("cases.db")
    curs = conn.cursor()

    curs.execute("""SELECT "ID" FROM "CASE_DETAIL" WHERE "STATUS" NOT IN
                ('Final Disposition', 'Transferred', 'Bankruptcy', 'Judgment Released',
                'Judgment Satisfied', 'Appealed', 'Final Status', 'Dismissed')""")
    active_case_nums = [tup[0] for tup in curs.fetchall()]
    curs.close()

    for table_name in ["CASE_DETAIL", "EVENT", "DISPOSITION"]:
        drop_rows_from_table(table_name, active_case_nums)

    return active_case_nums

@click.command()
@click.argument("afterdate", nargs=1)
@click.argument("beforedate", nargs=1)
@click.argument("outfile", default="results.json")
@click.option('--showbrowser / --headless', default=False, help='whether to operate in headless mode or not')

# performs a full 'scraper run' between afterdate and beforedate - gets case details, events, and dispoitions for all case nums between
# afterdate and beforedate, also updates rows in event/disposition/case_detail table that are still active
def parse_filings(afterdate, beforedate, outfile, showbrowser=False):
    # use default firefox browser - use the commented line instead once you move helpers to another file
    if showbrowser:
        # fetch_page.driver = webdriver.Firefox()
        driver = webdriver.Firefox()

    all_case_nums = get_all_case_nums(afterdate, beforedate) + get_old_active_case_nums()

    # save case nums as csv, give to parse_all function - may be a more normal way to do this
    # all_case_nums_df = pd.DataFrame(all_case_nums)
    all_case_nums_df.to_csv("temp_cases.csv", header=False, index=False)
    os.system(f"python3 parse_hearings.py temp_cases.csv {outfile}")
    # uncomment if you want to keep the csv
    # os.remove("temp_cases.csv")

if __name__ == "__main__":
    parse_filings()
