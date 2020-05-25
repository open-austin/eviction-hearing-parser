# eviction-hearing-parser

Parse registers of actions for Travis County eviction hearings

This command line utility takes a register of actions in the HTML format [published by Travis County](odysseypa.traviscountytx.gov), and extracts information about the last scheduled hearing in the register (regardless of whether the hearing is in the past or future). It can output a CSV collecting this information from many HTML files.

To use `eviction-hearing-parser`, download the HTML records that interest you from the county website, and collect them in a folder. (A script to help you do this has not yet been written).

Then, install Python on your computer. Python version 3.8 is suggested.

Make a copy of the `eviction-hearing-parser` repository and navigate to it using the command line.

On the command line in the `eviction-hearing-parser` directory, create a virtual environment with the command:

`python3 -m venv venv`

Activate the virtual environment with the command:

`source venv/bin/activate`

Install the required libraries with:

`pip install -r requirements.txt`

Install Firefox with [geckodriver](https://github.com/mozilla/geckodriver/releases) as described in the [Selenium documentation](https://selenium-python.readthedocs.io/installation.html).

Then execute the command line utility with a command in this format:

`python parse_hearings.py [your input directory] [name of new output file]`

For instance, if you use the following command to scrape the three Case IDs included in `test_input.csv`:

`python parse_hearings.py test_input.csv result.json`

...then you'll create a new file called `result.json` with scraped data from those three cases.
