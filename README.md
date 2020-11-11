# eviction-hearing-parser

Parse registers of actions for Travis County court hearings and calendar data, with a focus on eviction hearings.

[![open-austin](https://circleci.com/gh/open-austin/eviction-hearing-parser.svg?style=svg)](https://app.circleci.com/pipelines/github/open-austin/eviction-hearing-parser)
[![Coverage Status](https://coveralls.io/repos/github/open-austin/eviction-hearing-parser/badge.svg?branch=master)](https://coveralls.io/github/open-austin/eviction-hearing-parser?branch=master)

Front-end dashboard / other relevant links? link to the website from which we're scraping.
For instructions on using the scraper, just keep reading. For instructions on contrubuting to this project, click [here](#instructions-for-contributing-developers).

### Command Line Tools Instructions

First, some setup:

1) Clone this GitHub repo to your local computer.

1) Download [Chromedriver](https://chromedriver.chromium.org/downloads) and put it in the root directory of this project.

2) Get a local database [set up](#database-set-up-instructions).

3) Install Python3 (3.8 suggested) if you don't already have it. Windows instructions [here](#windows-instructions-for-python-beginners), mac [here](https://docs.python-guide.org/starting/install3/osx/).

4) Navigate to your `eviction-hearing-parser` direcotry in the command line.

5) Create and a virtual environment using the command:
`python3 -m venv venv`
If you'd rather not use a virtual environment, that should work too, and you can skip this step and the next one as well.

6) Activate the virtual environment with the command:
`source venv/bin/activate`

7) Install the required libraries with:
`pip install -r requirements.txt`

Now for the fun part! We have 5 command line tools:

#### Parse Hearings
delete email lines if you don't have that - describe this as well in the .env section, just say that if you want to get emails, but chances are you won't need it. also need to see whether the google sheets stuff affects this and the other scripts


To use this command line utility, feed in a "CSV" file containing a series of case ID numbers on separate lines. The scraper will fetch the register of actions for each case from the database [published by Travis County](https://odysseypa.traviscountytx.gov/JPPublicAccess/default.aspx). Then it extracts information about the last scheduled hearing in the register (regardless of whether the hearing is in the past or future). It will output a JSON file collecting this information for each of the case IDs.

Create a CSV file with a list of case IDs that you want to query (check out `test_input.csv` in this repo for an example of how this file should look).

Then execute the command line utility with a command in this format:

`python parse_hearings.py [your input CSV file] [name of new output file]`

For instance, if you use the following command to scrape the three case IDs included in `test_input.csv`:

`python parse_hearings.py test_input.csv result.json`

...then you'll create a new file called `result.json` with scraped data from those three cases.

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

#### Parse Settings

#### Parse Filings
delete email lines if you don't have that

#### Parse filings and settings since date
delete email lines if you don't have that

#### Schedule
delete email lines if you don't have that



### Database Set Up Instructions

#### Setting up a local PostgreSQL Database

#### Creating the database schema
1) Use pg_restore:

2) Run create scripts:

#### PgAdmin Set Up (optional)


### .env File Instructions
Create a .env file in the root directory of the project, and add the following two lines:
```
LOCAL_DEV=true
LOCAL_DATABASE_URL=postgres://localhost/your_local_database_name
```

### Instructions for Contributing Developers

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
 10. Download the [Precompiled Binaries for Windows] (https://www.sqlite.org/download.html) corresponding to your machine. Create a folder called C:\sqlite and extract the files from the download to this folder.
 11. Add the folder containing the geckodriver.exe, and C file to your PATH. To do this, type "Edit the system environment variables" in the start menu, select it, then click "Environment Variables" in System Properties. Select "Path", click "Edit..." , then "New", then add the folder containing geckodriver.exe and click OK, then do the same for C:\sqlite
 12. In the command line, while in the eviction-hearing-parser folder, type the command:
`sqlite3 cases.db "$(cat sql/*)"`
