import awswrangler as wr
import boto3
from dotenv import load_dotenv
import pandas as pd
import os

from liftingcast import LiftingCast

# set up aws stuff
print("Initializing environment")
load_dotenv()
region = os.environ.get("AWS_REGION")
lifter_table_name = os.environ.get("AWS_DYNAMO_TABLE_NAME")
boto3.setup_default_session(region_name=region)

# fetch lifters
print("Scraping lifters")
L = LiftingCast()
L.fetch_meets()
L.fetch_lifters()
scraped_lifters = pd.DataFrame(L.lifters)

# lifters that we are currently storing
print("Fetching lifters from dynamo")
stored_lifters = wr.dynamodb.read_items(
    table_name=lifter_table_name, allow_full_scan=True
)

# create two dataframes for each action we need to do
lifters_to_delete = pd.DataFrame()
lifters_to_insert = pd.DataFrame()
if "lifter_id" in scraped_lifters.columns and "lifter_id" in stored_lifters.columns:
    lifters_to_delete = stored_lifters[
        ~stored_lifters.lifter_id.isin(scraped_lifters.lifter_id)
    ]
    lifters_to_insert = scraped_lifters[
        ~scraped_lifters.lifter_id.isin(stored_lifters.lifter_id)
    ]

# delete any lifters we are currenlty storing that we did not scrape
print(f"{len(lifters_to_delete.index)} lifters to delete")
if "lifter_id" in lifters_to_delete.columns:
    wr.dynamodb.delete_items(
        items=lifters_to_delete.to_dict("records"), table_name=lifter_table_name
    )

# insert any lifters we scraped that we are currently not storing
print(f"{len(lifters_to_insert.index)} lifters to insert")
if "lifter_id" in lifters_to_insert.columns:
    wr.dynamodb.put_df(df=lifters_to_insert, table_name=lifter_table_name)

print("DONE")
