import os
import click
import fetch_page
from hearing import fetch_filings
from persist import get_old_active_case_nums
from selenium import webdriver

# returns list of all case nums for all prefixes between afterdate and beforedate
def get_all_case_nums(afterdate: str, beforedate: str):
    case_num_prefixes = ["J1-CV-20*", "J2-CV-20*", "J3-EV-20*", "J4-CV-20*", "J5-CV-20*"]
    all_case_nums = []
    for prefix in case_num_prefixes:
        prefix_case_nums = fetch_filings(afterdate, beforedate, prefix)
        all_case_nums += prefix_case_nums
    return all_case_nums

@click.command()
@click.argument("afterdate", nargs=1)
@click.argument("beforedate", nargs=1)
@click.argument("outfile", default="results.json")
@click.option('--showbrowser / --headless', default=False, help='whether to operate in headless mode or not')

# Performs a full 'scraper run' between afterdate and beforedate - gets case details, events, and dispositions for all case nums between
# afterdate and beforedate. Example of date format - 9/1/2020. Also updates rows in event/disposition/case_detail table that are still active
def parse_filings(afterdate, beforedate, outfile, showbrowser=False):
    # use default firefox browser (rather than headless) is showbrowser is True
    showbroser_str = ""
    if showbrowser:
        fetch_page.driver = webdriver.Firefox()
        showbroser_str = "--showbrowser"

    all_case_nums = get_all_case_nums(afterdate, beforedate) + get_old_active_case_nums()

    # create temporary csv with one case number per line to feed to parse_hearings
    with open("temp_cases.csv", 'w') as myfile:
        for case_num in all_case_nums:
            myfile.write(case_num + "\n")
    os.system(f"python3 parse_hearings.py temp_cases.csv {outfile} {showbroser_str}")
    # comment if you want to keep the csv
    os.remove("temp_cases.csv")

if __name__ == "__main__":
    parse_filings()
