__author__ = "Guy Mosseri"

import sqlite3


class Friend:
    def __init__(self, friend_id, name, password):
        self.friend_id = friend_id
        self.name = name
        self.password = password

    def __str__(self):
        return f"{self.__dict__}"

    def __eq__(self, other):
        return self.name == other.name


class Balance:
    def __init__(self, first_id, second_id, balance):
        self.first_id = first_id
        self.second_id = second_id
        self.balance = balance

    def __eq__(self, other):
        if not isinstance(other, Balance):
            return NotImplemented
        return self.first_id == other.first_id and self.second_id == other.second_id

    def get_friends(self, db):
        first = db.get_friend_by_id(self.first_id)
        second = db.get_friend_by_id(self.second_id)
        return [first, second]


class Transaction:
    def __init__(self, tx_id, sender_id, receiver_id, amount, status="PENDING", time=0):
        self.id = tx_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.amount = amount
        self.status = status
        self.time = time


class Nickname:
    def __init__(self, nicker_id, nicked_id, nickname):
        self.nicker_id = nicker_id
        self.nicked_id = nicked_id
        self.nickname = nickname


class Friend_of:
    def __init__(self, friend: Friend, balance: Balance, nickname: Nickname):
        self.id = friend.friend_id
        self.name = friend.name
        self.balance = balance.balance if self.id == balance.second_id else -balance.balance
        self.nickname = nickname.nickname

    def __repr__(self):
        return f"{self.__dict__}"


class Session:
    def __init__(self, session_id, friend_id):
        self.session_id = session_id
        self.friend_id = friend_id

    def __repr__(self):
        return f"{self.__dict__}"


class App_ORM:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._ensure_tables()

    def _open_DB(self):
        self.conn = sqlite3.connect(
            "database.db",
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.cursor = self.conn.cursor()

    def _close_DB(self):
        if self.conn:
            self.conn.close()

    def _commit(self):
        self.conn.commit()

    def _execute(self, sql, *argv):
        self.cursor.execute(sql, argv)

    def _ensure_tables(self):
        sqls = [
            """CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                password TEXT NOT NULL
            );
            """,
            """CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
            
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,

                status TEXT NOT NULL,
            
                amount REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
                FOREIGN KEY (sender_id) REFERENCES friends(id),
                FOREIGN KEY (receiver_id) REFERENCES friends(id)
            );""",
            """CREATE TABLE IF NOT EXISTS balances (
                friend1_id INTEGER NOT NULL,
                friend2_id INTEGER NOT NULL,
            
                balance REAL NOT NULL DEFAULT 0,
            
                PRIMARY KEY (friend1_id, friend2_id),
            
                FOREIGN KEY (friend1_id) REFERENCES friends(id),
                FOREIGN KEY (friend2_id) REFERENCES friends(id)
            );""",
            """CREATE TABLE IF NOT EXISTS nicknames (
                nicker_id INTEGER NOT NULL,
                nicked_id INTEGER NOT NULL,

                nickname TEXT NOT NULL,

                PRIMARY KEY (nicker_id, nicked_id),

                FOREIGN KEY (nicker_id) REFERENCES friends(id),
                FOREIGN KEY (nicked_id) REFERENCES friends(id)
            );""",
            """CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                friend_id INTEGER NOT NULL,
                FOREIGN KEY (friend_id) REFERENCES friends(id)
            );
            """
        ]
        self._open_DB()
        for sql in sqls:
            self._execute(sql)
        self._commit()
        self._close_DB()

    def delete_table(self, table_name):
        sql = f"DELETE FROM {table_name}"
        sql2 = "DELETE FROM sqlite_sequence WHERE name=?"
        self._open_DB()
        self._execute(sql)
        self._execute(sql2, table_name)
        self._commit()
        self._close_DB()
        print("deleted "+table_name)

    # ----------- Friends ----------- #
    def insert_friend(self, friend: Friend):
        sql = """
            INSERT INTO friends (name, password)
            VALUES (?, ?)
        """
        self._open_DB()
        self._execute(sql, friend.name, friend.password)
        self._commit()
        self._close_DB()

    def get_all_ids(self):
        sql = "SELECT id FROM friends"
        self._open_DB()
        self._execute(sql)
        rows = self.cursor.fetchall()
        self._close_DB()
        return [row[0] for row in rows]

    def get_friend_id_by_name(self, name):
        sql = "SELECT id FROM friends WHERE name=?"
        self._open_DB()
        self._execute(sql, name)
        row = self.cursor.fetchone()
        self._close_DB()
        return row[0] if row else None

    def get_name_by_friend_id(self, friend_id):
        sql = "SELECT name FROM friends WHERE id=?"
        self._open_DB()
        self._execute(sql, friend_id)
        row = self.cursor.fetchone()
        self._close_DB()
        return row[0] if row else None

    def friend_exists(self, name):
        sql = "SELECT EXISTS(SELECT 1 FROM friends WHERE name=?)"
        self._open_DB()
        self._execute(sql, name)
        exists = self.cursor.fetchone()[0] == 1
        self._close_DB()
        return exists

    def validate_friend(self, name, password):
        sql = "SELECT EXISTS(SELECT 1 FROM friends WHERE name=? AND password=?)"
        self._open_DB()
        self._execute(sql, name, password)
        valid = self.cursor.fetchone()[0] == 1
        self._close_DB()
        return valid

    def get_friends_of(self, id):
        sql = "SELECT * FROM friends WHERE id!=?"
        self._open_DB()
        self._execute(sql, id)
        rows = self.cursor.fetchall()
        self._close_DB()
        return [Friend(*row) for row in rows]

    # ----------- Balances ----------- #
    def insert_balance(self, balance: Balance):
        sql = "INSERT INTO balances (friend1_id, friend2_id, balance) VALUES (?, ?, ?)"
        self._open_DB()
        self._execute(sql, balance.first_id,
                      balance.second_id, balance.balance)
        self._commit()
        self._close_DB()

    def get_balances_for_friend_id(self, friend_id):
        sql = "SELECT * FROM balances WHERE friend1_id=? OR friend2_id=?"
        self._open_DB()
        self._execute(sql, friend_id, friend_id)
        rows = self.cursor.fetchall()
        self._close_DB()
        return [Balance(*row) for row in rows]

    def update_balance(self, friend1_id, friend2_id, amount):
        sql = "UPDATE balances SET balance=balance+? WHERE friend1_id=? AND friend2_id=?"
        self._open_DB()
        self._execute(sql, amount, friend1_id, friend2_id)
        self._commit()
        self._close_DB()

    # ----------- Transactions ----------- #
    def insert_transaction(self, tx: Transaction):
        sql = "INSERT INTO transactions (sender_id, receiver_id, amount, status) VALUES (?, ?, ?, ?)"
        self._open_DB()
        self._execute(sql, tx.sender_id, tx.receiver_id, tx.amount, tx.status)
        self._commit()
        self._close_DB()

    # ----------- Nicknames ----------- #
    def insert_nickname(self, nickname: Nickname):
        sql = "INSERT INTO nicknames (nicker_id, nicked_id, nickname) VALUES (?, ?, ?)"
        self._open_DB()
        self._execute(sql, nickname.nicker_id,
                      nickname.nicked_id, nickname.nickname)
        self._commit()
        self._close_DB()

    def nickname_exists(self, nicker_id, nicked_id):
        sql = "SELECT EXISTS(SELECT 1 FROM nicknames WHERE nicker_id=? AND nicked_id=?)"
        self._open_DB()
        self._execute(sql, nicker_id, nicked_id)
        exists = self.cursor.fetchone()[0] == 1
        self._close_DB()
        return exists

    def update_nickname(self, nickname: Nickname):
        sql = "UPDATE nicknames SET nickname=? WHERE nicker_id=? AND nicked_id=?"
        self._open_DB()
        self._execute(sql, nickname.nickname,
                      nickname.nicker_id, nickname.nicked_id)
        self._commit()
        self._close_DB()

    def get_nickname(self, nicker_id, nicked_id):
        sql = "SELECT * FROM nicknames WHERE nicker_id=? AND nicked_id=?"
        self._open_DB()
        self._execute(sql, nicker_id, nicked_id)
        row = self.cursor.fetchone()
        self._close_DB()
        return Nickname(*row) if row else None

    # ----------- Sessions ----------- #
    def insert_session(self, session: Session):
        sql = "INSERT INTO sessions (session_id, friend_id) VALUES (?, ?)"
        self._open_DB()
        self._execute(sql, session.session_id, session.friend_id)
        self._commit()
        self._close_DB()

    def session_exists(self, session_id):
        sql = "SELECT EXISTS(SELECT 1 FROM sessions WHERE session_id=?)"
        self._open_DB()
        self._execute(sql, session_id)
        exists = self.cursor.fetchone()[0] == 1
        self._close_DB()
        return exists

    def delete_session(self, session_id):
        sql = "DELETE FROM sessions WHERE session_id=?"
        self._open_DB()
        self._execute(sql, session_id)
        self._commit()
        self._close_DB()

    def get_friend_id_from_session(self, session_id):
        sql = "SELECT friend_id FROM sessions WHERE session_id=?"
        self._open_DB()
        self._execute(sql, session_id)
        row = self.cursor.fetchone()
        self._close_DB()
        return row[0] if row else None
