from firebase_admin import messaging
from handlers.get_topic import user_id_to_topic


class Notification:
    def __init__(self):
        self.user_id = -1
        self.title = ""
        self.body = ""

    user_id: int
    title: str
    body: str

    def send(self):
        messaging.send(messaging.Message(
            notification=messaging.Notification(
                title=self.title, body=self.body),
            topic=user_id_to_topic(self.user_id)
        ))


class NotificationBuilder:
    def __init__(self):
        self.__notification = Notification()

    def transaction_received(self, sender_name) -> 'NotificationBuilder':
        self.__notification.title = "New Transaction"
        self.__notification.body = f"{sender_name} has sent you a new transaction, open the app to accept it"
        return self

    def with_user_id(self, user_id) -> 'NotificationBuilder':
        self.__notification.user_id = user_id
        return self

    def build(self) -> Notification:
        return self.__notification


# NotificationBuilder().with_user_id(2).alarm().build().send()
