import os
import json
from fastapi import FastAPI, Response, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from handlers.get_topic import user_id_to_topic
from handlers.api_funcs import *
from SQL_ORM import Transaction, Nickname

import firebase_admin
from firebase_admin import messaging, credentials
from firebase_admin.exceptions import FirebaseError


class TokenPayload(BaseModel):
    token: str


class TransactionRequest(BaseModel):
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


firebase_creds = json.loads(os.environ.get("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(firebase_creds)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)


ensure_balances()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "https://7z7crp38-5173.uks1.devtunnels.ms",
                   "https://vamosbrazil.netlify.app",
                   "https://vamos-frontend-liart.vercel.app",
                   "https://vamos-frontend-meowmeow8888s-projects.vercel.app"],
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


@app.post("/api/me")
def api_me(session_id: str | None = Cookie(default=None)):
    id = convert_cookie(session_id)
    return {"id": id}


@app.post("/api/device-token")
def api_device_token(token: TokenPayload, session_id: str | None = Cookie(default=None)):
    id = convert_cookie(session_id)

    print(f"DEBUG: Received token: '{token.token}'")

    if not token.token:
        print("error: No FCM token provided")
        raise HTTPException(status_code=400, detail="No FCM token provided")

    try:
        response = messaging.subscribe_to_topic(
            [token.token], user_id_to_topic(id))
        response2 = messaging.subscribe_to_topic([token.token], "all")

        if response.success_count > 0:
            print(f"Subscribed user {id} to personal topic successfully")
        if response.failure_count > 0:
            print(
                f"Failed to subscribe to personal topic: {response.errors[0].reason}")

        if response2.success_count > 0:
            print("Subscribed to 'all' successfully")
        if response2.failure_count > 0:
            print(
                f"Failed to subscribe to 'all': {response2.errors[0].reason}")

        return {}

    except FirebaseError as e:
        print(f"Firebase Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/friends")
def api_friends(session_id: str | None = Cookie(default=None)):
    id = convert_cookie(session_id)

    friends = get_friends(id)
    return {"friends": friends}


@app.post("/api/create-transaction")
def api_transactions(tx: TransactionRequest, session_id: str | None = Cookie(default=None)):
    id = convert_cookie(session_id)
    print(f"from: {id}, to: {tx.receiverId}, amount: {tx.amount}")
    transaction = Transaction(0, id, tx.receiverId, tx.amount)
    handle_create_transaction(transaction)
    return {}


@app.post("/api/nickname")
def api_nickname(nickname: NicknameRequest, session_id: str | None = Cookie(default=None)):
    id = convert_cookie(session_id)

    handle_nickname(Nickname(nickname.nickerId,
                    nickname.nickedId, nickname.nickname))
    return {}
