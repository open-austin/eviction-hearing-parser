import os
import sys
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from arcgis import join_features
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
from connect_to_database import get_database_connection
from statuses import statuses_map
from emailing import log_and_email

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)

load_dotenv()
engine = get_database_connection()
ARCGIS_USERNAME, ARCGIS_PASSWORD = os.getenv("ARCGIS_USERNAME"), os.getenv("ARCGIS_PASSWORD")

# overwrites the table/feature layer named old_csv_name using new_df
# only works if new_df has the same columns as the old feature/table
# create an existing feature layer by manually uploading a csv to arcGIS and selecting the "Publish this file as a hosted layer" option
def overwrite_csv(username, password, new_df, old_csv_name):
    gis = GIS(url='https://www.arcgis.com', username=username, password=password)

    csv_file_name = f"{old_csv_name}.csv"
    new_df.to_csv(csv_file_name, index=False)

    old_item = gis.content.search(f"title: {old_csv_name}", 'Feature Layer')[0]
    old_feature_layer = FeatureLayerCollection.fromitem(old_item)

    logger.info(f"Overwriting feature layer named '{old_csv_name}'.... there will now be {len(new_df)} features.")
    overwrite_response = old_feature_layer.manager.overwrite(csv_file_name)
    logger.info(f'Done overwriting feature layer. Response: {overwrite_response}')

    os.remove(csv_file_name)


def create_dates_df():
    sql_query = """
                WITH filings_table AS (
                    SELECT count(case_number) AS filings_count, TO_DATE("date", 'MM/DD/YYYY') AS f_date
                    FROM v_case
                    WHERE "date" != ''
                    GROUP BY f_date )

                SELECT filing_counts_by_date.f_date AS "DATE", filing_counts_by_date.filings_count AS "FILINGS COUNT",
                   filing_counts_by_date.cum_count AS "CUMULATIVE COUNT", judgment_counts_by_date.judgments AS "JUDGMENTS"
                   FROM (
                	    SELECT
                	    f_date, filings_count,
                	    SUM(filings_count) OVER (ORDER BY f_date ASC rows BETWEEN unbounded preceding AND current row) AS cum_count
                	    FROM filings_table) AS filing_counts_by_date
            	   JOIN (
            	        SELECT COUNT(status) AS judgments, to_date("date", 'MM/DD/YYYY') AS j_date
            		    FROM v_case
            	        WHERE LOWER(status) IN
                	    ('final status', 'judgment satisfied',
                	    'pending writ return', 'judgment released',
                	    'final disposition', 'pending writ')
            		     AND "date" != ''
            	         GROUP BY j_date) AS judgment_counts_by_date
            	   ON filing_counts_by_date.f_date = judgment_counts_by_date.j_date
                """
    return pd.read_sql(sql_query, con=engine)

def create_zips_csv():
    sql_query = """
                SELECT plaintiff_zip AS "ZIP_Code", COUNT(*) AS "Number_of_Filings"
                FROM case_detail
                WHERE plaintiff_zip != ''
                GROUP BY plaintiff_zip
                """
    return pd.read_sql(sql_query, con=engine)

def create_precincts_csv():
    sql_query = """
                SELECT
                SUBSTRING(case_number, 1, 1) || 'P-' || SUBSTRING(case_number, 2, 1) AS "Precinct_1",
                SUBSTRING(case_number, 2, 1) AS "Precinct",
                COUNT(*) AS "Count"
                FROM case_detail
                GROUP BY "Precinct_1", "Precinct"
                """
    return pd.read_sql(sql_query, con=engine)

def create_jpdata_csv():

    def handle_null(expected_string):
        if pd.isnull(expected_string):
            return ""
        else:
            return expected_string

    def case_active_or_inactive(case):
        substatus = handle_null(case["Substatus"]).lower()
        if substatus in statuses_map:
            return "Active" if statuses_map[substatus]["is_active"] else "Inactive"
        else:
            log_and_email(f"Can't figure out whether {case['Case_Num']} is active or inactive because '{substatus}' is not in our statuses map dictionary.", "Encountered Unknown Substatus", error=True)
            return None

    def get_case_status(case):
        substatus = handle_null(case["Substatus"]).lower()
        if substatus in statuses_map:
            return statuses_map[substatus]["status"]
        else:
            log_and_email(f"Can't figure out the Status column of the JPData csv for {case['Case_Num']} because '{substatus}' is not in our statuses map dictionary.", "Encountered Unknown Substatus", error=True)
            return None

    def get_month_value(case):
        disposition_date = case["disposition_date"]
        status = handle_null(case["Status"]).lower()

        if not disposition_date:
            return None

        disposition_date = datetime.strptime(disposition_date, "%m/%d/%Y")
        march_14 = datetime(2020, 3, 14)

        return "Y" if (disposition_date >= march_14) and (status == "judgment") else "N"

    sql_query = """
                SELECT DISTINCT ON (cases.case_number)
                cases.case_number as "Case_Num", status as "Substatus", setting_date as "Hearing Date", date AS disposition_date
                FROM
                	(SELECT c.case_number, status, date
                	 FROM case_detail AS c
                	 INNER JOIN
                	(SELECT
                	 case_number, date
                	 FROM disposition) AS d
                	 ON c.case_number = d.case_number) AS cases
                LEFT JOIN
                	(SELECT setting_date, case_number
                	 FROM setting) AS settings
                	 ON cases.case_number = settings.case_number
                ORDER BY "Case_Num", setting_date
                """

    jpdata = pd.read_sql(sql_query, con=engine)
    jpdata["Active_Inactive"] = jpdata.apply(lambda case: case_active_or_inactive(case), axis=1)
    jpdata["Status"] = jpdata.apply(lambda case: get_case_status(case), axis=1)
    jpdata["Month"] = jpdata.apply(lambda case: get_month_value(case), axis=1)
    jpdata = jpdata.drop(columns=["disposition_date"])

    jpdata.to_csv("data.csv")

    return jpdata
create_jpdata_csv()
def overwrite_table_and_join(username, password, new_df, table_name, other_table_name, table_join_field, other_join_field, joined_table_name):
    gis = GIS(url='https://www.arcgis.com', username=username, password=password)
    overwrite_csv(ARCGIS_USERNAME, ARCGIS_PASSWORD, new_df, table_name)

    new_table = gis.content.search(f"title: {table_name}", 'Feature Layer')[0].tables[0]
    layer_to_join = gis.content.search(f"title: {other_table_name}", 'Feature Layer')[0].layers[0]

    joined_layer = join_features(new_table, layer_to_join, attribute_relationship=[{"targetField": table_join_field, "joinField": other_join_field}])
    joined_layer_df = joined_layer.query().sdf

    overwrite_csv(ARCGIS_USERNAME, ARCGIS_PASSWORD, joined_layer_df, joined_table_name)

# do it for zips and precincts
# overwrite_table_and_join(ARCGIS_USERNAME, ARCGIS_PASSWORD, create_zips_csv(), "zips_test", "Travis County ZIP Codes_WFL1", "ZIP_Code", "ZCTA5CE10", "test_join_zips")
# overwrite_table_and_join(ARCGIS_USERNAME, ARCGIS_PASSWORD, create_precincts_csv(), "precincts_test", "Justice_of_the_Peace_and_Constable_Precincts", "Precinct_1", "Precinct_1", "test_join")
