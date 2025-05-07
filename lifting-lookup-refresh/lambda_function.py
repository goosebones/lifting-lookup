import json
import boto3
import boto3.dynamodb
import boto3.dynamodb.table
import requests
from datetime import datetime
import re
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

region = os.environ.get("AWS_REGION")
boto3.setup_default_session(region_name=region)
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

LIFTER_TABLE = os.environ['AWS_DYNAMO_LIFTER_TABLE_NAME']
LIFTER_UPDATE_TABLE = os.environ['AWS_DYNAMO_LIFTER_UPDATE_TABLE_NAME']
VIP_SUBSCRIPTION_TABLE = os.environ['AWS_DYNAMO_VIP_LIFTER_SUBSCRIPTION_TABLE_NAME']


def fetch_meets():
    """ Get meets from liftingcast """
    response = requests.get("https://liftingcast.com/api/meets")
    meets = response.json()["docs"]

    return [meet for meet in meets if 'showOnHomePage' in meet and meet["showOnHomePage"]]


def get_lifters_from_meet(meet: Dict):
    """ Get list of lifters for a meet """
    meet_id = meet['_id']
    # lifter documents always start with "l".
    # query only couchdb documents beginning with "l" to avoid downloading other document types
    response = requests.get(
        f"https://couchdb.liftingcast.com/{meet_id}_readonly/_all_docs",
        params={
            'include_docs': 'true',
            'startkey': '"l"',
            'endkey': '"l\ufff0"'
        }
    )
    meet_docs = response.json()
    lifters = []

    for doc in meet_docs["rows"]:
        try:
            if "name" in doc["doc"]:
                lifters.append({
                    "lifter_name": doc["doc"]["name"],
                    "lifter_id": doc["id"],
                    "meet_id": meet["_id"],
                    "meet_name": meet["name"],
                    "meet_date": meet["date"]
                })
        except Exception as e:
            print(f"Error processing document: {e}")
    
    return lifters


def fetch_lifters(meet_list: List[Dict]):
    """ Fetch lifters from a list of meets """
    all_lifters = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_lifters_from_meet, meet) for meet in meet_list]
        for future in futures:
            all_lifters.extend(future.result())

    return all_lifters


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


def get_lifter_insertions_deletions(scraped_lifters: List[Dict], stored_lifters: List[Dict]):
    """ Get differences between screped_lifters and stored_lifters """    
    scraped_ids = {lifter['lifter_id'] for lifter in scraped_lifters}
    stored_ids = {lifter['lifter_id'] for lifter in stored_lifters}
    
    to_delete = [lifter for lifter in stored_lifters if lifter['lifter_id'] not in scraped_ids]
    to_insert = [lifter for lifter in scraped_lifters if lifter['lifter_id'] not in stored_ids]
    
    return to_insert, to_delete


def bulk_insert(items: List[Dict], table):
    """ insert items into DynamoDB table using bulk writer """
    with table.batch_writer() as writer:
        for item in items:
            writer.put_item(Item=item)


def bulk_delete(items: List[Dict], table):
    """ delete items from DynamoDB table using bulk writer """
    table_key_schema = table.key_schema
    keys = [
        {schema['AttributeName']: item[schema['AttributeName']] 
         for schema in table_key_schema}
        for item in items
    ]
    with table.batch_writer() as writer:
        for key in keys:
            writer.delete_item(Key=key)


def generate_notification_list(subscriptions: List[Dict], new_lifters: List[Dict]):
    """ Generate list of notifications """
    def scrub_lifter_name(name: str):
        return re.sub(r'[\d\s-]+', '', name).lower()

    notifications = []
    current_date = datetime.now()
    
    for subscription in subscriptions:
        subscriber_email = subscription['subscriber_email']
        subscription_names = subscription.get('subscription_list', [])
        
        for lifter in new_lifters:
            if not lifter.get('lifter_name'):
                continue
                
            scrubbed_lifter_name = scrub_lifter_name(lifter['lifter_name'])
            for sub_name in subscription_names:
                if scrub_lifter_name(sub_name) == scrubbed_lifter_name:
                    meet_date = datetime.strptime(lifter['meet_date'], '%m/%d/%Y')
                    if meet_date >= current_date:
                        notifications.append({
                            'subscriber_email': subscriber_email,
                            **lifter
                        })
    
    return notifications


def send_notification_emails(notifications: List[Dict]):
    """ Send email notifications using SES """
    if not notifications:
        return
        
    # Group notifications by email
    email_groups = {}
    for notification in notifications:
        email = notification['subscriber_email']
        if email not in email_groups:
            email_groups[email] = []
        email_groups[email].append(notification)
    
    # Send emails
    for email, lifter_notifications in email_groups.items():
        body = f"""
        <p>Greetings {email},</p>
        <p>This notification is to alert you of the following lifters registering for a meet:</p>
        <ul>
        """
        for lifter in lifter_notifications:
            body += f"""<li>{lifter['lifter_name']} - <a href="https://liftingcast.com/meets/{lifter['meet_id']}/lifter/{lifter['lifter_id']}/info">{lifter['meet_name']}</a></li>"""
        
        body += f"""
        </ul>
        <p>To update your VIP Lifter Notification settings, please visit <a href="liftinglookup.com/account/vip">LiftingLookup</a>.
        You can also reply directly to this email with any issues or concerns.</p>
        """
        
        try:
            ses.send_email(
                Source='vip-notification@liftinglookup.com',
                Destination={
                    'ToAddresses': [email],
                    'BccAddresses': ['vip-notification@liftinglookup.com']
                },
                Message={
                    'Subject': {'Data': 'LiftingLookup VIP Lifter Notification'},
                    'Body': {'Html': {'Data': body}}
                }
            )
        except Exception as e:
            print(f"Error sending email to {email}: {e}")

def lambda_handler(event, context):
    """Main Lambda handler function."""
    try:
        # get our tables ready
        lifter_table = dynamodb.Table(LIFTER_TABLE)
        lifter_update_table = dynamodb.Table(LIFTER_UPDATE_TABLE)
        vip_subscription_table = dynamodb.Table(VIP_SUBSCRIPTION_TABLE)

        # Fetch and process lifters
        print('fetching meets')
        meets = fetch_meets()
        print('scraping lifters')
        scraped_lifters = fetch_lifters(meets)
        print('getting stored lifters')
        stored_lifters = get_full_table(lifter_table)
        
        # Update DynamoDB
        insertions, deletions = get_lifter_insertions_deletions(scraped_lifters, stored_lifters)
        print('inserting lifters')
        bulk_insert(insertions, lifter_table)
        print('deleting lifters')
        bulk_delete(deletions, lifter_table)
        print('making record of this update')
        bulk_insert(
            items=[{
                'update_datetime': datetime.now().isoformat(),
                'insertion_count': len(insertions),
                'deletion_count': len(deletions)
            }],
            table=lifter_update_table
        )
        
        # Handle VIP notifications
        print('getting subscriptions')
        subscriptions = get_full_table(vip_subscription_table)
        notifications = generate_notification_list(subscriptions, insertions)
        print('sending emails')
        send_notification_emails(notifications)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully refreshed lifter data',
                'insertion_count': len(insertions),
                'deletion_count': len(deletions)
            })
        }
    except Exception as e:
        print(f"Error in Lambda function: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error refreshing lifter data',
                'error': str(e)
            })
        }
