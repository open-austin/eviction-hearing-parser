# eviction-hearing-parser

Parse registers of actions for Travis County court hearings and calendar data.

[![open-austin](https://circleci.com/gh/open-austin/eviction-hearing-parser.svg?style=svg)](https://app.circleci.com/pipelines/github/open-austin/eviction-hearing-parser)
[![Coverage Status](https://coveralls.io/repos/github/open-austin/eviction-hearing-parser/badge.svg?branch=master)](https://coveralls.io/github/open-austin/eviction-hearing-parser?branch=master)

The data is scraped from Travis County's official [judicial records](https://odysseypa.traviscountytx.gov/JPPublicAccess/default.aspx), and is being used to create this [dashboard](https://trla.maps.arcgis.com/apps/opsdashboard/index.html#/8f5beb8367f44d30aa2ed6eeb2b3b3e4), and to support the Eviction Solidarity Network's court tracking efforts where volunteers track court hearings to ensure that tenant protections are being enforced and tenants are connected to resources.  Additionally, the data will be used to help analyze trends in evictions to target campaigns towards repeat, bad actor landlords and craft policy solutions to combat the eviction crisis. 

For instructions on using the scraper, just keep reading. For instructions on contrubuting to this project, see the [instructions for developers](#instructions-for-contributing-developers). If you have any questions or experience any problems using this, contact Matt (matt@openaustin.org) and/or Alex (apiazza@trla.org).
<br/><br/><br/>

### Command Line Tools Instructions

First, some setup:

1) Clone this GitHub repository to your local computer.

2) Download [Chromedriver](https://chromedriver.chromium.org/downloads) and put it in the root directory of this project.

3) [Set up](#database-set-up-instructions) a local PostgreSQL database.

4) Install Python3 (3.8 suggested) if you don't already have it. Windows instructions [here](#windows-instructions-for-python-beginners), mac [here](https://docs.python-guide.org/starting/install3/osx/).

5) Navigate to your `eviction-hearing-parser` directory in the command line.

6) Create a virtual environment using the command:
`python3 -m venv venv` <br/>
If you'd rather not use a virtual environment, that should work too, and you can skip steps 6 and 7.

7) Activate the virtual environment with the command:
`source venv/bin/activate`

8) Install the required libraries with:
`pip install -r requirements.txt`

One more note - web scraping can be finnicky, and we've tried to anticipate and handle any errors that may occur, but you may experience errors sometimes. When you do, just re-run the same command a few times, or try re-running it without the `--showbrowser` option, and it should work eventually. If not, or if the errors are frequent, let us know!

Now for the fun part! We have 5 command line tools:

#### 1) Parse Hearings
To use this command line utility, feed in a "CSV" file containing a series of case ID numbers on separate lines. The scraper will fetch the register of actions for each case from the database [published by Travis County](https://odysseypa.traviscountytx.gov/JPPublicAccess/default.aspx). Then it extracts information about the last scheduled hearing in the register (regardless of whether the hearing is in the past or future). It will output a JSON file collecting this information for each of the case IDs. Step-by-step instructions:

1) Create a CSV file with a list of case IDs that you want to query (check out `test_input.csv` in this repo for an example of how this file should look).

2) In the project directory and with your virtual environment activated, execute the command line utility with a command in this format:

`python parse_hearings.py [your input CSV file] [name of new output file]`

For instance, if you use the following command to scrape the three case IDs included in `test_input.csv`:

`python parse_hearings.py test_input.csv result.json`

If you want to see your Chrome browser in action, add the `--showbrowser` command. For example:

`python parse_hearings.py test_input.csv result.json --showbrowser`

3) A new file called `result.json` will appear in your project directory with scraped data from those three cases, the data for these cases will be added to your database tables (specifically the case_detail, disposition, and event tables).

#### 2) Parse Settings
This command line utility scrapes court calendar data from a specified date range using the Court Calendar link on Travis County's [website](https://odysseypa.traviscountytx.gov/JPPublicAccess/default.aspx). Only settings with category "Civil" are scraped.

For example, the command

`python parse_settings.py afterdate beforedate result.json`

will scrape all settings on or after `afterdate` and on or before `beforedate` (dates should be formatted like: mm-dd-yyy), output results to `result.json`, and add the appropriate rows to the setting table in your database. For example:

`python parse_settings.py 9-1-2020 9-7-2020 result.json`

Add `--showbrowser` to the end of the command to see the browser as it is scraping:

`python parse_settings.py 9-1-2020 9-7-2020 result.json --showbrowser`

#### 3) Parse Filings
This tool does the same thing as Parse Hearings, except its input is a date range rather than a CSV with case numbers (it finds all the case numbers in the given date range and scrapes their data rather than being told the case numbers). It will also look in your database for still active cases and rescrape those. This way if a case has new data it will be updated in your database.

So, the command

`python parse_filings.py  9-1-2020 9-7-2020 result.json`

will scrape data for all cases that occurred on or aftr September 1, 2020 and on or before September 7, 2020. To do the same thing while showing the browser, use:

`python parse_filings.py  9-1-2020 9-7-2020 result.json --showbrowser`

#### 4) Schedule
This script allows you to automatically run the scraper repeatedly on a schedule. The command

`python schedule.py`

will start the schedule. When the schedule is running, it will perform a "scraper run" every day at 3:00AM EST. Each scraper run performs the same exact tasks as Parse Filings and Parse Settings, except that no .json files are created and there is no `--showbrowser` option.

As the code is currently set up, the scraper calls Parse Filings with today's date as the `beforedate` and seven days ago as the `afterdate`, and it calls Parse Settings with seven days ago as `afterdate` and 90 days from now as `beforedate`. These parameters, as well as the time and frequency at which the scraper runs, can be adjusted with minor adjustments to the `schedule.py` script. For example, changing

`sched.add_job(scrape_filings_and_settings_task, 'interval', days=1, start_date='2020-10-12 03:00:00', timezone='US/Eastern')`

to

`sched.add_job(scrape_filings_and_settings_task, 'interval', days=7, start_date='2020-10-12 03:00:00', timezone='US/Eastern')`

will cause the scraper to run every 7 days rather than every day.

For as long as you don't exit the process, the schedule will continue to run locally. But if you want it to run even when your computer is off, you can do what we do - [use Heroku](#using-heroku-to-schedule-scraper-runs).

#### 5) Parse Filings and Settings Since Date
Given a date, this script will populate your database will all of the hearings and settings data on or after the given date and on or before the current date. It also divides the tasks up into weeks, so if one week fails it can just move onto the next week. Once it's done it will print to the console all the weeks for which it failed. If you've set up an email account for this project, as described [here](#.env-file-instructions), it will also email you the weeks that failed.

For example, the command

`python get_all_filings_settings_since_date.py  9-1-2020`

gets all data from September 1, 2020 up until the current date.
<br/><br/><br/>

### Instructions for Contributing Developers

1) Fork this project's repository and clone it to your local computer.

2) [Set up](#database-set-up-instructions) a local PostgreSQL database.

3) [Create](#environment-variable-instructions) your .env file.

4) Set up a virtual environment, install requirements, and install chromedriver as described [here](#command-line-tools- instructions).

5) Write code.

5) Make sure the scraper still works by running the tests in the tests folder and making sure the command line tools (parse_hearings.py, parse_settings.py, parse_filings.py) successfully populate the database and don't throw errors. To run the tests, just use the command `pytest`.

6) Ideally, add your own tests (if it makes sense to do so).

7) When you're done, make a pull request from your fork. If the PR completes a specific issue, include
"closes #issue_number" in the description of your PR.
<br/><br/><br/>

### Database Set Up Instructions

If you're using this scraper to get data, follow the instructions below. We're working on making an option to use these tools without having a database, but haven't done that quite yet. If you're a developer contributing to the project, you can also follow these instructions, or you can skip them and follow the instructions [here](#for-developers-test-database-uri), which is quicker and easier but also slightly less ideal.

#### Setting up a Local PostgreSQL Instance
1) Setup PostgresQL. Tutorials for MacOS users [here](https://www.postgresqltutorial.com/install-postgresql-macos/) and [here](https://www.robinwieruch.de/postgres-sql-macos-setup). For Windows users [here](https://www.postgresqltutorial.com/install-postgresql/).

2) Create a local database by entering `createdb desired_database_name` in the command line.

3) Add the schema to your database using the command `pg_restore -O -x -c -d database_name_from_previous_step evictions_dump.dump`. The file `evictions_dump.dump` can be found in the "sql" folder of this project. When running this command, make sure you're in the same directory as this file. You may see an error message or two, but that should be fine.

4) If using `pg_restore` didn't work, you can run the commands in each of the .sql files in the "sql" folder to create all the necessary tables, indexes, views, and constraints.

#### pgAdmin Set Up (optional)
[pgAdmin](https://www.pgadmin.org/) can be useful to access your database in a web browser. Here's how to get set up with that. For first time users, specifically ones adding a local server, these instructions may not be perfect, but hopefully they'll help.

1) Install [pgAmin4](https://www.pgadmin.org/download/) on your computer.

1) Once you have a pgAdmin window open, click on Add New Server.

1) Give the server a name under General, then go to Connection and fill out the first 5 fields (host, port, database, user, password) according to your database credentials. If it's just a local server, which it probably is unless you're accessing the [test database](#test-database-uri), you may only have to fill out some of these fields.

1) Click Save and you should see the server on the left. Click on it, then click Databases, then scroll until you find the one that matches your database name.

1) Click on that, then Schemas, then Tables, then any of the table names, and you can see all the column names and some other info.

1) To see the actual data, click on the Query Tool (should be on the top left, and looks like a lightning bolt). You can then query the data using SQL. For example, `SELECT * FROM setting` will show you all the data in the setting table.
<br/><br/><br/>

### Environment Variable Instructions
Create a file named ".env" in the root directory of this project, and add the following two lines:
```
LOCAL_DEV=true
LOCAL_DATABASE_URL=postgres://localhost/your_local_database_name
```

If you'd like to receive error emails, create a new Gmail account and configure it to [allow less secure apps](https://devanswers.co/allow-less-secure-apps-access-gmail-account/). Then add the following two lines to your .env file:
```
ERROR_EMAIL_ADDRESS=your_email_address
ERROR_EMAIL_ADDRESS_PASSWORD=your_password
```

#### Test Database Uri
If you're a developer choosing to use the test database rather than set up a local database, set `LOCAL_DATABSE_URL` to `test_database_uri`. The URI is kind of a secret and changes periodically, so email Alex at alexpiazza2000@gmail.com to get it. The drawback of this method is that if many people are using the test database, any data you add for testing purposes may be removed / changed.
<br/><br/><br/>

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
<br/><br/><br/>

### Using Heroku to Schedule Scraper Runs
No instructions yet... try Google for now :)
