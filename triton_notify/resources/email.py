import datetime
import logging
import os

from notifiers import get_notifier
import boto3
from botocore.exceptions import ClientError

from flask import current_app as app
from flask import render_template


class Email:
    def __init__(self, message_data, request_obj):
        self.message_data = message_data
        self.request_obj = request_obj
        self.sender = message_data.get("sender")
        self.recipient = message_data.get("recipient")
        self.subject = message_data.get("subject", "New Notification Triton")
        self.message = message_data.get("message")
        self.message_html = message_data.get("message_html")
    
    def __len__(self):
        return len(self.message)

    def __repr__(self):
        return "{!r}({!r})".format(self.__class__.__name__, self.message_data)

    def send_message(self):
        if not all([self.message, self.sender, self.recipient]):
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Invalid Request:{self.message_data} | {self.request_obj.remote_addr}"
            )
            return {
                "message_status": "Not Sent",
                "status_message": "Invalid Request",
                "status_code": 400,
            }

        if not self.message_html:
            self.message_html = self.apply_template(self.message)
        status = self.send_email_ses(
            self.recipient, self.sender, self.subject, self.message, self.message_html
        )
        return status

    def apply_template(self, message):
        template = render_template("base_email_template.html", message=message)
        return template

    def send_email_ses(self, recipient, sender, subject, message, message_html):
        region_name = os.environ.get("AWS_REGION_NAME", "us-east-1")
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        charset = "UTF-8"

        if not all([aws_access_key_id, aws_secret_access_key]):
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | AWS keys not set; message_data:{self.message_data} | {self.request_obj.remote_addr}"
            )
            return {
                "message_status": "Not Sent",
                "status_message": "Server Error",
                "status_code": 500,
            }
        client = boto3.client("ses", region_name=region_name)
        try:
            response = client.send_email(
                Destination={"ToAddresses": [recipient]},
                Message={
                    "Body": {
                        "Html": {"Charset": charset, "Data": message_html},
                        "Text": {"Charset": charset, "Data": message},
                    },
                    "Subject": {"Charset": charset, "Data": subject},
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
        else:
            return {
                "message_status": "Sent",
                "status_message": "Message Sent Successfully",
                "status_code": 200,
            }
