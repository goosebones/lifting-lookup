import boto3
import json
from dotenv import load_dotenv
import os

load_dotenv()
lifter_table_name = os.environ.get("AWS_DYNAMO_LIFTER_TABLE_NAME")
update_lifter_table_name = os.environ.get("AWS_DYNAMO_LIFTER_UPDATE_TABLE_NAME")
region = os.environ.get("AWS_REGION")
dynamodb = boto3.resource("dynamodb", region_name=region)
table = dynamodb.Table(lifter_table_name)
update_history_table = dynamodb.Table(update_lifter_table_name)


def lambda_handler(event, context):
    res = table.scan()
    data = res["Items"]

    while "LastEvaluatedKey" in res:
        res = table.scan(ExclusiveStartKey=res["LastEvaluatedKey"])
        data.extend(res["Items"])

    update_res = update_history_table.scan()
    updates = update_res["Items"]
    sorted_updates = sorted(updates, key=lambda x: x["update_datetime"])
    most_recent_update = sorted_updates[-1]["update_datetime"]

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "data": {"lifters": json.dumps(data), "last_updated": most_recent_update},
    }
