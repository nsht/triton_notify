import datetime
import logging
import os

from notifiers import get_notifier
import boto3

from flask import current_app as app


class Email:
    def __init__(self, message_data, request_obj):
        self.message_data = message_data
        self.request_obj = request_obj
        self.sender = message_data.get("sender")
        self.recipient = message_data.get("recipient")
        self.subject = message_data.get("subject", "New Notification Triton")
        self.message = message_data.get("message")
        self.body_html = message_data.get("message_html")
        self.region_name = os.environ.get("AWS_REGION_NAME", "us-east-1")
        self.aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.charset = "UTF-8"

    def send_message(self):
        if not all([self.aws_access_key_id, self.aws_secret_access_key]):
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | AWS keys not set; message_data:{self.message_data} | {self.request_obj.remote_addr}"
            )
            return {
                "message_status": "Not Sent",
                "status_message": "Server Error",
                "status_code": 500,
            }

        if not all([self.message, self.sender, self.recipient]):
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Invalid Request:{self.message_data} | {self.request_obj.remote_addr}"
            )
            return {
                "message_status": "Not Sent",
                "status_message": "Invalid Request",
                "status_code": 400,
            }

        if not self.body_html:
            self.body_html = self.apply_template(self.message)
        client = boto3.client("ses", region_name=self.region_name)
        try:
            response = client.send_email(
                Destination={"ToAddresses": [self.recipient]},
                Message={
                    "Body": {
                        "Html": {"Charset": self.charset, "Data": self.body_html},
                        "Text": {"Charset": self.charset, "Data": self.message},
                    },
                    "Subject": {"Charset": self.charset, "Data": self.subject},
                },
                Source=self.sender,
            )
        except ClientError as e:
            return {
                "message_status": "Not Sent",
                "status_message": "Unable to send message reason:{}".format(
                    e.response["Error"]["Message"]
                ),
                "status_code": 500,
            }
            print(e.response["Error"]["Message"])
        else:
            return {
                "message_status": "Sent",
                "status_message": "Message Sent Successfully",
                "status_code": 200,
            }

    # TODO improve templte and function
    def apply_template(self, message):
        template = f"""<html>
        <body>
        <p>{message}</p>
        </body>
        </html>"""
        return template
