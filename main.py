from fastapi import FastAPI, Response, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware

from handlers.api_funcs import *
from SQL_ORM import Transaction, Nickname
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
# http://87.71.152.73:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/login")
def api_login(name, password, res: Response):
    session_id = login(name, password)
    if not session_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    res.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,      # True in production with HTTPS
        samesite="lax",    # or "none" if frontend is on another origin over HTTPS
        max_age=60 * 60 * 24 * 30,  # 300 days
    )
    return {}


@app.get("/api/me")
def me(session_id: str | None = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401)

    id = me(session_id)
    if not id:
        raise HTTPException(status_code=401)

    return {"id": id}


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
