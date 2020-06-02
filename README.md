# eviction-hearing-parser

Parse registers of actions for Travis County eviction hearings

[![open-austin](https://circleci.com/gh/open-austin/eviction-hearing-parser.svg?style=svg)](https://app.circleci.com/pipelines/github/open-austin/eviction-hearing-parser)

To use this command line utility, feed in a "CSV" file containing a series of case ID numbers on separate lines. The scraper will fetch the register of actions for each case from the database [published by Travis County](https://odysseypa.traviscountytx.gov/JPPublicAccess/default.aspx). Then it extracts information about the last scheduled hearing in the register (regardless of whether the hearing is in the past or future). It will output a JSON file collecting this information for each of the case IDs.

To use `eviction-hearing-parser`, install Python on your computer. Python version 3.8 is suggested.

Make a copy of the `eviction-hearing-parser` repository and navigate to it using the command line.

On the command line in the `eviction-hearing-parser` directory, create a virtual environment with the command:

`python3 -m venv venv`

Activate the virtual environment with the command:

`source venv/bin/activate`

Install the required libraries with:

`pip install -r requirements.txt`

Install Firefox with [geckodriver](https://github.com/mozilla/geckodriver/releases) as described in the [Selenium documentation](https://selenium-python.readthedocs.io/installation.html).

Create a CSV file with a list of case IDs that you want to query (check out `test_input.csv` in this repo for an example of how this file should look).

Then execute the command line utility with a command in this format:

`python parse_hearings.py [your input CSV file] [name of new output file]`

For instance, if you use the following command to scrape the three case IDs included in `test_input.csv`:

`python parse_hearings.py test_input.csv result.json`

...then you'll create a new file called `result.json` with scraped data from those three cases.
