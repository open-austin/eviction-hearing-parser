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

Create the sqlite database schema:

`sqlite3 cases.db "$(cat sql/*)"`

Install Firefox with [geckodriver](https://github.com/mozilla/geckodriver/releases) as described in the [Selenium documentation](https://selenium-python.readthedocs.io/installation.html).

Create a CSV file with a list of case IDs that you want to query (check out `test_input.csv` in this repo for an example of how this file should look).

Then execute the command line utility with a command in this format:

`python parse_hearings.py [your input CSV file] [name of new output file]`

For instance, if you use the following command to scrape the three case IDs included in `test_input.csv`:

`python parse_hearings.py test_input.csv result.json`

...then you'll create a new file called `result.json` with scraped data from those three cases.

### Windows Instructions for Python Beginners: 
#### Installation instructions: 
 1. If Python is not already installed on your computer, download and install python. If you will not be doing much coding with python, it may be easier to check "Add Python to Path" during installation. 
 2. Clone Eviction Hearing Parser from github. If you do not have git installed locally, you can click the green "Code" button, download the script as a .zip file, and extract it to a local folder. (However, it is recommended to set up git be able to easily download updates in the future)
 3. Navigate to the eviction-hearing-parser folder using the command line. You can do this by typing "cmd" in the start menu, and opening the "Command Prompt" app, then typing
 `cd path_to_file` (where path_to_file is the folder location)
 4. Create a virtual environment called "venv" for the app to run in by typing the following command in the command prompt: 
 `python -m venv venv`
 (This will let us install python libraries just for Eviction Hearing Parser without changing the default python installed on the machine) 
 5. Activate the virtual environment "venv" with the command 
`venv\Scripts\activate` .
 6. You should now see (venv) before your line in the command line. Install the custom libraries for Eviction Hearing Parser with the command 
`pip install -r requirements.txt`
 7. When the installation is complete (you should see "Successfully installed"), type the command `deactivate` to close the virtual environment
 8. Install [Firefox](https://www.mozilla.org/en-US/firefox/) on your machine (if it is not already installed)
 9. Download the [geckodriver](https://github.com/mozilla/geckodriver/releases) zip file for windows. Extract the .exe file to a folder on your PC
 10. Add the folder containing the geckodriver.exe file to your PATH. To do this, type "Edit the system environment variables" in the start menu, select it, then click "Environment Variables" in System Properties. Select "Path", click "Edit..." , then "New", then add the folder containing geckodriver.exe and click OK. 

#### Instructions to use the script: 
1. Create a CSV file with a list of case IDs that you want to query (check out `test_input.csv` in this repo for an example of how this file should look).
2. Save the CSV file to the eviction-hearing-parser folder
3. Navigate to the folder using the command line. You can do this by typing "cmd" in the start menu, and opening the "Command Prompt" app, then typing
 `cd path_to_file` (where path_to_file is the folder location)
 4. Activate the virtual environment "venv" with the command 
`venv\Scripts\activate`
5. Execute the command line utility with a command in this format:
`python parse_hearings.py [your input CSV file] [name of new output file]`For instance, the following command will scrape the three case IDs included in `test_input.csv`:
`python parse_hearings.py test_input.csv result.json`
6. When the command is finished, the result file can be found in the eviction-hearing-parser folder.