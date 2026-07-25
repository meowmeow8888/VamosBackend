from SQL_ORM import *
import secrets
from handlers.notification_sender import NotificationBuilder


class FriendOf:
    def __init__(self, friend: Friend, balance: Balance, nickname: Nickname):
        self.id = friend.friend_id
        self.name = friend.name
        self.balance = balance.balance if self.id == balance.second_id else -balance.balance
        self.nickname = nickname.nickname

    def __repr__(self):
        return f"{self.__dict__}"


class PendingTransaction:
    def __init__(self, tx_id, sender_name, amount, created_at):
        self.txId = tx_id
        self.senderName = sender_name
        self.amount = amount
        self.createdAt = created_at

    def __repr__(self):
        return f"{self.__dict__}"


def get_highers(id, ids):
    highers = []
    for i in ids:
        if i > id:
            highers.append(i)
    return highers


def ensure_balances():
    db = App_ORM()
    ids = db.get_all_ids()
    for id in ids:
        balances = db.get_balances_for_friend_id(id)
        highers = get_highers(id, ids)
        if highers:
            for missing in highers:
                balance = Balance(id, missing, 0)
                if balance not in balances:
                    db.insert_balance(balance)


def get_friends(id):
    db = App_ORM()
    friends = db.get_friends_of(id)
    balances = db.get_balances_for_friend_id(id)

    friends_of = []
    for f, b in zip(friends, balances):
        if db.nickname_exists(id, f.friend_id):
            nickname = db.get_nickname(id, f.friend_id)
        else:
            nickname = Nickname(id, f.friend_id, "")
        friends_of.append(FriendOf(f, b, nickname))
    return friends_of


def handle_nickname(nickname: Nickname):
    db = App_ORM()
    if db.nickname_exists(nickname.nicker_id, nickname.nicked_id):
        db.update_nickname(nickname)
    else:
        db.insert_nickname(nickname)


def create_session(friend_id):
    session_id = secrets.token_hex(32)
    session = Session(session_id, friend_id)
    return session


def login(name, password):
    db = App_ORM()
    name = " ".join(name.split())
    if not db.friend_exists(name):
        db.insert_friend(Friend(0, name, password))
        ensure_balances()
    if not db.validate_friend(name, password):
        return None
    f_id = db.get_friend_id_by_name(name)
    session = create_session(f_id)
    db.insert_session(session)
    return session.session_id


def logout(session_id):
    db = App_ORM()
    db.delete_session(session_id)


def me(session_id):
    db = App_ORM()
    if not db.session_exists(session_id):
        return None
    return db.get_friend_id_from_session(session_id)


def handle_create_transaction(tx: Transaction):
    db = App_ORM()
    db.insert_transaction(tx)
    sender_name = db.get_name_by_friend_id(tx.sender_id)
    NotificationBuilder().with_user_id(
        tx.receiver_id).transaction_received(sender_name).build().send()


def get_pending(id):
    db = App_ORM()
    transactions = db.get_pending_transactions(id)
    pending = [PendingTransaction(tx.id, db.get_name_by_friend_id(
        tx.sender_id), -tx.amount, tx.time) for tx in transactions]
    return pending


def accept_transaction(id, tx_id):
    db = App_ORM()
    db.change_status(tx_id, "ACCEPTED")
    tx = db.get_transaction_by_id(tx_id)
    print(f"tx: {tx}")
    if tx.sender_id < tx.receiver_id:
        db.update_balance(tx.sender_id, tx.receiver_id, tx.amount)
    else:
        db.update_balance(tx.receiver_id, tx.sender_id, -tx.amount)
    name = db.get_name_by_friend_id(id)
    NotificationBuilder().with_user_id(id).transaction_accepted(name).build().send()


def decline_transaction(id, tx_id):
    db = App_ORM()
    db.change_status(tx_id, "DECLINED")
    name = db.get_name_by_friend_id(id)
    NotificationBuilder().with_user_id(id).transaction_declined(name).build().send()


def get_tx_history(id):
    db = App_ORM()
