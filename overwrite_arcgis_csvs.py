from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
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

    print(f"Overwriting feature layer named '{old_csv_name}'.... there will now be {len(new_df)} features.")
    old_feature_layer.manager.overwrite(csv_file_name)
    print('Done overwriting feature layer.')

    os.remove(csv_file_name)

df = pd.DataFrame({"A": [1, 2, 3, 4], "B": [4, 5, 6, 7]})
overwrite_csv(ARCGIS_USERNAME, ARCGIS_PASSWORD, df, "a fake csv")
