from dotenv import load_dotenv
import os

load_dotenv()
local_dev = os.getenv("LOCAL_DEV") == "true"

# supported values for county: travis, williamson
county = os.getenv("COUNTY")
if county:
    county = county.lower()
