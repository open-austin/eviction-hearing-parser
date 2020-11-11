#Running the code

##On the cloud (Heroku)
-Install Heroku CLI
-Login with our credentials
`heroku login`
-Do other stuff that Alex knows to set up your code with your heroku

##Access using pgAdmin (download instructions here). 
-Once you have a pgAdmin window open, click on Add New Server.  
-Give it a name under General, then go to Connection and fill out the first 5 fields (host, port, database, user, password) according to our database credentials on Heroku.  
-You can leave everything else blank. Then click Save and you should see the server on the left. Click on it, then click Databases, then you'll have to scroll through all of them until you find the one that matches our database name.  
-Click on that, then Schemas, then Tables, then any of the table names, and you can see all the column names and some other info.  
-To see the actual data, click on the Query Tool (should be on the top left, and looks like a lightning bolt). You can then query the data using SQL – for example, `select * from table_name` will show you all the data in the table named table_name.  
-Our database credentials are retrievable on Heroku. From the dashboard, click for-db, then click Resources at the top, then click Heroku Postgres, and you'll see the info about the database. Then go to Settings and click View Credentials. 

##Running the scraper code locally:
-Install reqs:
`pip install -r requirements.txt`
-Setup Postgres [good tutorial here](https://www.robinwieruch.de/postgres-sql-macos-setup)
-Start Postgres `pg_ctl -D /usr/local/var/postgres start`
-createdb eviction-scraper
-Add Users to your new DB 
`psql eviction-scraper
CREATE ROLE xsqpbwotuzlraq;
ALTER ROLE "xsqpbwotuzlraq" WITH LOGIN;
CREATE ROLE postgres;
ALTER ROLE “postgres” WITH LOGIN;
pg_restore -O -x -c -d your_local_database_name evictions_dump.dump` (not sure if you have to do the above any more with this command)
-Make a .env file and set LOCAL_DATABASE_URL to the connection string of either your local database (use `psql \conninfo` (to get info to make url `postgresql://[user[:password]@][netloc][:port][,...][/dbname][?param1=value1&...]`) and LOCAL_DEV=true
-Set up google sheets api and share edit capabilities with the user email you create in credentials [good tutorial here](https://researchremix.wordpress.com/2019/01/03/gsheets-from-python/)
-Edit the code in gsheet.py init_sheets function to point to your json google credentials

And to do a scraper run, enter in command line:

`python parse_filings.py 8-24-2020 8-28-2020 results.json`

to run it for days between 8/24/2020 and 8/28/2020, inclusive, outputting results both to Postgres and locally to results.json. If you add --showbrowser to the end of the command it will show the scraping happening in chrome.

