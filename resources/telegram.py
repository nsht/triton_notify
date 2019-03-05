import datetime
import logging

from notifiers import get_notifier
from flask import current_app as app


class Telegram:
    def __init__(self, message_data, request_obj):
        print(message_data)
        self.message_data = message_data
        self.request_obj = request_obj
        self.message = message_data.get("message")
        self.token = message_data.get("token")
        self.chat_id = message_data.get("chat_id")

    def __len__(self):
        return len(self.message)

    def __repr__(self):
        return "{!r}({!r})".format(self.__class__.__name__, self.message_data)

    def send_message(self):
        if not all([self.message, self.token, self.chat_id]):
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Invalid Request:{self.message_data} | {self.request_obj.remote_addr}"
            )
            return {
                "message_status": "Not Sent",
                "status_message": "Invalid Request",
                "status_code": 400,
            }
        telegram = get_notifier("telegram")
        message_status = telegram.notify(
            message=self.message, token=self.token, chat_id=self.chat_id
        )
        if message_status.errors:
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Unable to send:{message_status.errors[0]} | {self.request_obj.remote_addr}"
            )
            return {
                "message_status": "Not Sent",
                "status_message": "Unable to send message reason:{}".format(
                    message_status.errors[0]
                ),
                "status_code": message_status.response.status_code,
            }
        app.logger.info(
            f"{datetime.datetime.utcnow().isoformat()} | Telegram message sent:{self.message} | {self.request_obj.remote_addr}"
        )
        return {
            "message_status": "Sent",
            "status_message": "Message Sent Successfully",
            "status_code": message_status.response.status_code,
        }
