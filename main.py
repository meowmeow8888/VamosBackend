from fastapi import FastAPI, Response, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware

from handlers.api_funcs import *
from SQL_ORM import Transaction, Nickname
from pydantic import BaseModel
from firebase_admin import messaging
from handlers.get_topic import user_id_to_topic


class MeRequest(BaseModel):
    token: str


class TransactionRequest(BaseModel):
    senderId: int
    receiverId: int
    amount: float


class NicknameRequest(BaseModel):
    nickerId: int
    nickedId: int
    nickname: str


class LoginRequest(BaseModel):
    name: str
    password: str


def convert_cookie(session_id):
    if session_id is None:
        raise HTTPException(status_code=401)

    id = me(session_id)
    if not id:
        raise HTTPException(status_code=401)
    return id


ensure_balances()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "https://7z7crp38-5173.uks1.devtunnels.ms",
                   "https://vamosbrazil.netlify.app",
                   "https://vamos-frontend-liart.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/login")
def api_login(data: LoginRequest, res: Response):
    session_id = login(data.name, data.password)
    if not session_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    res.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,      # True in production with HTTPS, False for localhost
        # or "none" if frontend is on another origin over HTTPS, lax for localhost
        samesite="none",
        max_age=60 * 60 * 24 * 300,  # 300 days
    )
    return {}


@app.post("/api/logout")
def api_logout(session_id: str | None = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=401)

    logout(session_id)
    return {}


@app.get("/api/me")
def api_me(token: MeRequest, session_id: str | None = Cookie(default=None)):
    id = convert_cookie(session_id)
    messaging.subscribe_to_topic([token.token], user_id_to_topic(id))
    messaging.subscribe_to_topic([token.token], "all")

    return {"id": id}


@app.get("/api/friends")
def api_friends(session_id: str | None = Cookie(default=None)):
    id = convert_cookie(session_id)

    friends = get_friends(id)
    return {"friends": friends}


@app.post("/api/transactions")
def api_transactions(tx: TransactionRequest, session_id: str | None = Cookie(default=None)):
    id = convert_cookie(session_id)

    if tx.amount > 0:
        transaction = Transaction(0, tx.receiverId, tx.senderId, tx.amount)
    else:
        transaction = Transaction(0, tx.senderId, tx.receiverId, -tx.amount)
    handle_transaction(transaction)
    return {}


@app.post("/api/nickname")
def api_nickname(nickname: NicknameRequest, session_id: str | None = Cookie(default=None)):
    id = convert_cookie(session_id)

    handle_nickname(Nickname(nickname.nickerId,
                    nickname.nickedId, nickname.nickname))
    return {}
