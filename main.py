from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from handlers.api_funcs import *
from SQL_ORM import App_ORM, Transaction, Nickname
from pydantic import BaseModel


class TransactionRequest(BaseModel):
    senderId: int
    receiverId: int
    amount: float


class NicknameRequest(BaseModel):
    nickerId: int
    nickedId: int
    nickname: str


ensure_balances()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://87.71.152.73:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/friends")
def api_friends(name):
    friends = get_friends(name)
    return {"friends": friends}


@app.get("/api/id")
def api_id(name):
    id = get_my_id(name)
    return {"id": id}


@app.post("/api/transactions")
def api_transactions(tx: TransactionRequest):
    if tx.amount > 0:
        transaction = Transaction(0, tx.receiverId, tx.senderId, tx.amount)
    else:
        transaction = Transaction(0, tx.senderId, tx.receiverId, -tx.amount)
    handle_transaction(transaction)
    return {}


@app.post("/api/nickname")
def api_nickname(nickname: NicknameRequest):
    handle_nickname(Nickname(nickname.nickerId,
                    nickname.nickedId, nickname.nickname))
    return {}
