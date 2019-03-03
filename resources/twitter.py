import tweepy


class Twitter:
    def __init__(self, message_data, request_obj):
        print(message_data)
        self.message_data = message_data
        self.request_obj = request_obj
        self.message = message_data.get("message")
        self.account_handle = message_data.get("account_handle")
        self.consumer_key = message_data.get("consumer_key")
        self.consumer_secret= message_data.get("consumer_secret")
        

