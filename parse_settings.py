import csv
import simplejson as json
import os
import sys
from typing import Any, Dict, List
import datetime as dt
import click
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hearing
import fetch_page
import persist
import gsheet
import logging

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)


def get_days_between_dates(afterdate, beforedate):
    "return a list of individual days between two dates"

    #convert to datetime objects
    beforedate = dt.datetime.strptime(beforedate, '%m-%d-%Y')
    afterdate = dt.datetime.strptime(afterdate, '%m-%d-%Y')

    #get days between as int
    n_days = (beforedate - afterdate).days

    #return each individual day, including the last one
    return [(afterdate + dt.timedelta(days=i)).strftime('%m/%d/%Y') for i in range(n_days + 1)]

def make_setting_list(days_to_pull: List[str]) -> List[Dict[str, Any]]:
    #pull all settings, one day at a time
    pulled_settings = []
    for setting_day in days_to_pull:
        day_settings = hearing.fetch_settings(afterdate=setting_day, beforedate=setting_day)
        pulled_settings.extend(day_settings)
    return pulled_settings

# same as parse_settings but without comman line interface and showbrowser option outputs scrape results to a gsheet:Settings_scheduler
def parse_settings_on_cloud(afterdate, beforedate, write_to_sheets=True):
    logger.info(f"Parsing settings between {afterdate} and {beforedate}.")

    days_to_pull = get_days_between_dates(afterdate=afterdate, beforedate=beforedate)
    pulled_settings = make_setting_list(days_to_pull)
    for setting in pulled_settings:
        persist.rest_setting(setting)
#maybe make this cleaner in sql? future work
    if write_to_sheets:
        gsheet.write_data(gsheet.open_sheet(gsheet.init_sheets(),"Court_scraper_eviction_scheduler","eviction_scheduler"),gsheet.morning_afternoon(gsheet.combine_cols(gsheet.filter_df(gsheet.filter_df(pd.DataFrame(pulled_settings),'setting_type','Eviction'),'hearing_type','(Hearing)|(Trial)'),['case_number','setting_style'],'case_dets').drop_duplicates("case_number", keep="last")))


@click.command()
@click.argument(
    "afterdate", nargs=1
)
@click.argument("beforedate", nargs=1)

@click.argument("outfile", type=click.File(mode="w"), default="result.json")
@click.option('--showbrowser / --headless', default=False, help='whether to operate in headless mode or not')

# example date format: 9-1-2020
def parse_settings(afterdate, beforedate, outfile, showbrowser=False):
    # If showbrowser is True, use the default selenium driver
    if showbrowser:
        from selenium import webdriver
        fetch_page.driver = webdriver.Chrome("./chromedriver")

    days_to_pull = get_days_between_dates(afterdate=afterdate, beforedate=beforedate)
    pulled_settings = make_setting_list(days_to_pull)
    for setting in pulled_settings:
        persist.rest_setting(setting)
    gsheet.write_data(gsheet.open_sheet(gsheet.init_sheets(),"Court_scraper_eviction_scheduler","eviction_scheduler"),gsheet.morning_afternoon(gsheet.combine_cols(gsheet.filter_df(gsheet.filter_df(pd.DataFrame(pulled_settings),'setting_type','Eviction'),'hearing_type','(Hearing)|(Trial)'),['case_number','setting_style'],'case_dets').drop_duplicates("case_number", keep="last")))
    json.dump(pulled_settings, outfile)

if __name__ == "__main__":
#    parse_settings_on_cloud()
    parse_settings()

