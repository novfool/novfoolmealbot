import os
import hmac
import hashlib
import httpx
from fastapi import FastAPI, Request
from app.conversation import handle_message
from app.database import init_db

app = FastAPI()
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def health():
    return {"status": "ok", "message": "食物 Bot 運行中 🍱"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # 只處理一般文字訊息
    message = data.get("message") or data.get("edited_message")
    if not message:
        return "ok"

    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()
    if not text:
        return "ok"

    replies = handle_message(str(chat_id), text)

    async with httpx.AsyncClient() as client:
        for reply in replies:
            await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, **reply}
            )

    return "ok"
