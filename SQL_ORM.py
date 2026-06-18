__author__ = "Guy Mosseri"

import sqlite3


class Friend:
    def __init__(self, friend_id, name):
        self.friend_id = friend_id
        self.name = name

    def __str__(self):
        return f"{self.__dict__}"

    def __eq__(self, other):
        return self.name == other.name

class Balance:
    def __init__(self, first_id, second_id, balance):
        self.first_id = first_id
        self.second_id = second_id
        self.balance = balance

    def get_friends(self, db):
        first = db.get_friend_by_id(self.first_id)
        second = db.get_friend_by_id(self.second_id)
        return [first, second]

class Transaction:
    def __init__(self, payer_id, receiver_id, amount, time):
        self.payer_id = payer_id
        self.receiver_id = receiver_id
        self.amount = amount
        self.time = time

class Friend_of:
    def __init__(self, friend: Friend, balance: Balance):
        self.friend_id = friend.friend_id
        self.name = friend.name
        self.balance = balance.balance if self.friend_id == balance.second_id else -balance.balance
        

class App_ORM:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._ensure_tables()

    def open_DB(self):
        self.conn = sqlite3.connect(
            "database.db",
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.cursor = self.conn.cursor()

    def close_DB(self):
        if self.conn:
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def execute(self, sql, *argv):
        self.cursor.execute(sql, argv)

    def _ensure_tables(self):
        sqls = [
            """CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
            """,
            """CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
            
                payer_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
            
                amount REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
                FOREIGN KEY (payer_id) REFERENCES friends(id),
                FOREIGN KEY (receiver_id) REFERENCES friends(id)
            );""",
            """CREATE TABLE IF NOT EXISTS balances (
                friend1_id INTEGER NOT NULL,
                friend2_id INTEGER NOT NULL,
            
                balance REAL NOT NULL DEFAULT 0,
            
                PRIMARY KEY (friend1_id, friend2_id),
            
                FOREIGN KEY (friend1_id) REFERENCES friends(id),
                FOREIGN KEY (friend2_id) REFERENCES friends(id)
            );"""
        ]
        self.open_DB()
        for sql in sqls:
            self.execute(sql)
        self.commit()
        self.close_DB()

    # ----------- Friends ----------- #
    def insert_friend(self, friend: Friend):
        sql = """
            INSERT INTO friends (name)
            VALUES (?)
        """
        self.open_DB()
        self.execute(sql, friend.name)
        self.commit()
        self.close_DB()

    def get_friend_id_by_name(self, name):
        sql = "SELECT * FROM friends WHERE name=?"
        self.open_DB()
        self.execute(sql, name)
        row = self.cursor.fetchone()
        self.close_DB()
        return row[0] if row else None

    def get_friend_by_name(self, name):
        sql = "SELECT * FROM friends WHERE name=?"
        self.open_DB()
        self.execute(sql, name)
        row = self.cursor.fetchone()
        self.close_DB()
        return Friend(*row) if row else None

    def friend_exists(self, name):
        friend = self.get_friend_by_name(name)
        if friend:
            return True
        return False

    def get_friends_of(self, name):
        sql = "SELECT * FROM friends WHERE name!=?"
        self.open_DB()
        self.execute(sql, name)
        rows = self.cursor.fetchall()
        self.close_DB()
        return [Friend(*row) for row in rows]

    # ----------- Balances ----------- #
    def get_balances_for_friend_id(self, friend_id):
        sql = "SELECT * FROM balances WHERE friend1_id=? OR friend2_id=?"
        self.open_DB()
        self.execute(sql, friend_id, friend_id)
        rows = self.cursor.fetchall()
        self.close_DB()
        return [Balance(*row) for row in rows]

if __name__ == '__main__':
    db = App_ORM()
    table_name = "friends"

    db.open_DB()
    db.execute(f"DELETE FROM {table_name}")
    db.commit()
    db.close_DB()
    print("deleted", table_name)

    db._ensure_tables()

    db.insert_friend(Friend(0, "Guy Mosseri"))
    db.insert_friend(Friend(0, "Orr Sarid"))
    db.insert_friend(Friend(0, "Tamar Price"))
    db.insert_friend(Friend(0, "Dror Krieze"))
    db.insert_friend(Friend(0, "Mia shuster"))
    print("inserted new users")
