"""
Module to get setting details between two dates.
To perform a scraper run, use: python parse_settings.py afterdate beforedate
(dates in format (m)m-(d)d-yyyy)
"""

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


def get_days_between_dates(afterdate: str, beforedate: str):
    "Return a list of individual days between two dates"

    #convert to datetime objects
    beforedate = dt.datetime.strptime(beforedate, '%m-%d-%Y')
    afterdate = dt.datetime.strptime(afterdate, '%m-%d-%Y')

    #get days between as int
    n_days = (beforedate - afterdate).days

    #return each individual day, including the last one
    return [(afterdate + dt.timedelta(days=i)).strftime('%m/%d/%Y') for i in range(n_days + 1)]

def make_setting_list(days_to_pull: List[str]) -> List[Dict[str, Any]]:
    """Pulls all settings, one day at a time"""

    pulled_settings = []
    for setting_day in days_to_pull:
        day_settings = fetch_page.fetch_settings(afterdate=setting_day, beforedate=setting_day)
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
    for setting in pulled_settings:
        persist.rest_setting(setting)
    #maybe make this cleaner in sql? future work
    if write_to_sheets:
        gsheet.write_data(gsheet.open_sheet(gsheet.init_sheets(),"Court_scraper_eviction_scheduler","eviction_scheduler"),gsheet.morning_afternoon(gsheet.combine_cols(gsheet.filter_df(gsheet.filter_df(pd.DataFrame(pulled_settings),'setting_type','Eviction'),'hearing_type','(Hearing)|(Trial)'),['case_number','setting_style'],'case_dets').drop_duplicates("case_number", keep="last")))


def parse_settings(afterdate: str, beforedate: str, outfile: str, showbrowser=False):
    """Gets data for all settings between `afterdate` and `beforedate` and sends results to PostgreSQL database."""

    # If showbrowser is True, use the default selenium driver
    if showbrowser:
        from selenium import webdriver
        fetch_page.driver = webdriver.Chrome("./chromedriver")

    days_to_pull = get_days_between_dates(afterdate=afterdate, beforedate=beforedate)
    pulled_settings = make_setting_list(days_to_pull)
    return pulled_settings

@click.command()
@click.argument("afterdate", nargs=1)
@click.argument("beforedate", nargs=1)
@click.argument("outfile", type=click.File(mode="w"), default="result.json")
@click.option('--showbrowser / --headless', default=False, help='whether to operate in headless mode or not')
def parse_and_persist_settings(afterdate: str, beforedate: str, outfile: str, showbrowser=False):
    pulled_settings = parse_settings(afterdate, beforedate, outfile, showbrowser)
    for setting in pulled_settings:
        persist.rest_setting(setting)
    gsheet.write_data(gsheet.open_sheet(gsheet.init_sheets(), "Court_scraper_eviction_scheduler", "eviction_scheduler"), gsheet.morning_afternoon(gsheet.combine_cols(gsheet.filter_df(gsheet.filter_df(pd.DataFrame(pulled_settings),'setting_type','Eviction'),'hearing_type','(Hearing)|(Trial)'),['case_number','setting_style'],'case_dets').drop_duplicates("case_number", keep="last")))
    json.dump(pulled_settings, outfile)


if __name__ == "__main__":
    parse_and_persist_settings()
