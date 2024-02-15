import awswrangler as wr
import boto3
from dotenv import load_dotenv
import os
import re
from time import sleep


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


class DynamoVIPLifterSubscription:
    def __init__(self):
        self.vip_lifter_subscription_table_name = os.environ.get(
            "AWS_DYNAMO_VIP_LIFTER_SUBSCRIPTION_TABLE_NAME"
        )

    def get_vip_lifter_subscriptions(self):
        return wr.dynamodb.read_items(
            table_name=self.vip_lifter_subscription_table_name, allow_full_scan=True
        )

    def get_notification_list(self, subscriptions, lifters):
        def scrub_lifter_lifter_name(lifter):
            name = lifter["lifter_name"]
            scrubbed_name = re.sub(r"[\d\s-]+", "", name).lower()
            return scrubbed_name

        subscriptions.explode("subscription_list")
        subscriptions.rename(columns={"subscription_list": "lifter_name"}, inplace=True)
        lifters["scrubbed_lifter_name"] = lifters.apply(
            scrub_lifter_lifter_name, axis=1
        )
        subscriptions["scrubbed_lifter_name"] = subscriptions.apply(
            scrub_lifter_lifter_name, axis=1
        )

        notifications = subscriptions.merge(lifters, on="scrubbed_lifter_name")
        return notifications


class SESVIPLifterNotification:
    def __init__(self):
        self.email_client = boto3.client("ses")

    def generate_email_html(self, subscriber_email, lifter_notifications):
        body = f"""
        <p>Greetings {subscriber_email},</p>
        <p>This notification is to alert you of the following lifters registerting for a meet:</p>
        """
        for lifter in lifter_notifications:
            body += f"""<li>{lifter['lifter_name_y']} - <a href="{f'https://liftingcast.com/meets/{lifter['meet_id']}/lifter/{lifter['lifter_id']}/info'}">{lifter['meet_name']}</a></li>"""

        body += f"""
        <p>To update your VIP Lifter Notification settings, please visit <a href="liftinglookup.com/account/vip">LiftingLookup</a>.
        You can also reply directly to this email with any issues or concerns.</p>
        """
        return body

    def send_vip_lifter_notification_emails(self, notifications):
        emails_dict = {
            group_key: group_rows.to_dict(orient="records")
            for group_key, group_rows in notifications.groupby("subscriber_email")
        }
        for subscriber_email, lifter_notifications in emails_dict.items():
            print(
                f"SENDING EMAIL TO {subscriber_email} FOR {lifter_notifications.length} LIFTERS"
            )
            send_args = {
                "Source": "vip-notification@liftinglookup.com",
                "Destination": {"ToAddresses": [subscriber_email]},
                "Message": {
                    "Subject": {"Data": "LiftingLookup VIP Lifter Notification"},
                    "Body": {
                        "Html": {
                            "Data": self.generate_email_html(
                                subscriber_email, lifter_notifications
                            )
                        }
                    },
                },
            }
            try:
                self.email_client.send_email(**send_args)
                print(f"SUCCESSFULLY SENT EMAIL TO {subscriber_email}")
                sleep(0.5)
            except Exception as e:
                print(f"EXCEPTION WHEN SENDING EMAIL ({lifter_notifications}) - {e}")
