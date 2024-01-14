import awswrangler as wr
import boto3
from dotenv import load_dotenv
import os

print("Initializing environment")
load_dotenv()
region = os.environ.get("AWS_REGION")
boto3.setup_default_session(region_name=region)


class DynamoLifter:
    def __init__(self):
        self.lifter_table_name = os.environ.get("AWS_DYNAMO_LIFTER_TABLE_NAME")

    def get_lifters(self):
        return wr.dynamodb.read_items(
            table_name=self.lifter_table_name, allow_full_scan=True
        )

    def insert_lifters(self, lifters):
        wr.dynamodb.put_df(df=lifters, table_name=self.lifter_table_name)

    def delete_lifters(self, lifters):
        wr.dynamodb.delete_items(
            items=lifters.to_dict("records"), table_name=self.lifter_table_name
        )


class DynamoLifterUpdate:
    def __init__(self):
        self.lifter_update_table_name = os.environ.get(
            "AWS_DYNAMO_LIFTER_UPDATE_TABLE_NAME"
        )

    def insert_lifter_update(self, update_datetime, insertion_count, deletion_count):
        wr.dynamodb.put_items(
            items=[
                {
                    "update_datetime": update_datetime,
                    "insertion_count": insertion_count,
                    "deletion_count": deletion_count,
                }
            ],
            table_name=self.lifter_update_table_name,
        )
