from notifiers import get_notifier


class Telegram:
    def __init__(self, message_data):
        print(message_data)
        self.message_data = message_data
        self.message = message_data.get("message")
        self.token = message_data.get("token")
        self.chat_id = message_data.get("chat_id")

    def __len__(self):
        return len(self.message)

    def send_message(self):
        if not all([self.message, self.token, self.chat_id]):
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
            return {
                "message_status": "Not Sent",
                "status_message": "Unable to send message reason:{}".format(
                    message_status.errors[0]
                ),
                "status_code": message_status.response.status_code,
            }
        return {
            "message_status": "Sent",
            "status_message": "Message Sent Successfully",
            "status_code": message_status.response.status_code,
        }
