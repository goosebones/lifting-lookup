import boto3
import json
import os

region = os.environ.get("AWS_REGION")
dynamodb = boto3.resource("dynamodb", region_name=region)

LIFTER_TABLE = os.environ["AWS_DYNAMO_LIFTER_TABLE_NAME"]
LIFTER_UPDATE_TABLE = os.environ["AWS_DYNAMO_LIFTER_UPDATE_TABLE_NAME"]

table = dynamodb.Table(LIFTER_TABLE)
update_history_table = dynamodb.Table(LIFTER_UPDATE_TABLE)


def get_full_table(table):
    """ Get all items stored in a DynamoDB table """
    results = []
    last_evaluated_key = None
    
    while True:
        scan_kwargs = {}
        if last_evaluated_key:
            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
            
        response = table.scan(**scan_kwargs)
        results.extend(response.get('Items', []))
        
        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break
            
    return results


def lambda_handler(event, context):
    """AWS Lambda handler function"""
    try:
        # Get lifters data
        lifter_table = dynamodb.Table(LIFTER_TABLE)
        lifters = get_full_table(lifter_table)

        # Get update history
        lifter_update_table = dynamodb.Table(LIFTER_UPDATE_TABLE)
        lifter_updates = get_full_table(lifter_update_table)
        sorted_lifter_updates = sorted(lifter_updates, key=lambda x: x["update_datetime"])
        most_recent_lifter_update = sorted_lifter_updates[-1]["update_datetime"]

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'lifters': lifters,
                'last_updated': most_recent_lifter_update
            })
        }
            
    except Exception as e:
        print(f"Error in Lambda function: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
            },
            'body': json.dumps({
                'error': str(e)
            })
        }


