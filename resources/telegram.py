from notifiers import get_notifier


class Telegram:
    def __init__(self,message_data):
        print(message_data)
        self.message_data = message_data
        self.message = message_data.get("message")
        self.token = message_data.get("token")
        self.chat_id = message_data.get("chat_id")
        if not all([self.message,self.token,self.chat_id]):
            return {"message_status":False,"status_message":"Invalid Request","status_code":400}

    def send_message(self):
        print("message sent desu")
        telegram = get_notifier('telegram')
        message_status = telegram.notify(message=self.message,token=self.token,chat_id=self.chat_id)
        print(message_status)
        if message_status.errors:
            return {"message_status":False,"status_message":"Unable to send message","status_code":500}
        return {"message_status":True,"status_message":"Message Send Successfully","status_code":200}
