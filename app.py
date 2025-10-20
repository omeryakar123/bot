import asyncio, hmac, hashlib, urllib.parse, os, json, logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from db import init_db, upsert_user, submit_score, get_user_score, get_leaderboard

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------- LOGGING ----------
logging.basicConfig(level=logging.INFO)

# ---------- ENV ----------
load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = os.environ["WEBAPP_URL"]
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# ---------- TELEGRAM BOT ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name, user.last_name)
    kb = [[KeyboardButton("🎮 Oyunu Aç", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(
        f"Merhaba {user.first_name or ''}! 👋\n"
        "Aşağıdaki butonla oyunu hemen Telegram içinde açabilirsin.",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )


async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = get_user_score(update.effective_user.id)
    await update.message.reply_text(f"⭐ En iyi skorun: {score}")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_leaderboard()
    if not rows:
        await update.message.reply_text("Henüz skor tablosu boş 🕹️")
        return
    lines = [f"{i+1}. {name or 'Anonim'} — {score}" for i, (_, name, score) in enumerate(rows)]
    await update.message.reply_text("🏆 TOP 10\n" + "\n".join(lines))

# ---------- BOT UYGULAMASI ----------
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("me", me))
application.add_handler(CommandHandler("top", top))

# ---------- FASTAPI ----------
fastapi_app = FastAPI(title="Telegram WebApp Bot Backend")

class ScorePayload(BaseModel):
    initData: str = Field(...)
    score: int = Field(..., ge=0)

@fastapi_app.on_event("startup")
async def startup_event():
    """Uygulama başlatıldığında DB ve botu başlat."""
    init_db()

    async def run_bot():
        await application.run_polling(stop_signals=None, close_loop=False)

    asyncio.get_running_loop().create_task(run_bot())

@fastapi_app.get("/")
async def root():
    return {"ok": True, "bot": "running"}

# ---------- WEBAPP DOĞRULAMA ----------
def validate_telegram_data(init_data: str, token: str):
    parsed = urllib.parse.parse_qs(init_data, strict_parsing=True)
    if "hash" not in parsed:
        raise ValueError("Eksik hash")
    received_hash = parsed["hash"][0]
    kv = [f"{k}={v[0]}" for k, v in parsed.items() if k != "hash"]
    kv.sort()
    check_string = "\n".join(kv).encode()
    secret = hashlib.sha256(token.encode()).digest()
    calc_hash = hmac.new(secret, msg=check_string, digestmod=hashlib.sha256).hexdigest()
    if calc_hash != received_hash:
        raise ValueError("Geçersiz imza")
    user_json = parsed.get("user", [None])[0]
    return json.loads(user_json)

# ---------- API ----------
@fastapi_app.post("/api/submit_score")
async def submit_score_api(payload: ScorePayload):
    try:
        user = validate_telegram_data(payload.initData, BOT_TOKEN)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    upsert_user(user["id"], user.get("username"), user.get("first_name"), user.get("last_name"))
    submit_score(user["id"], payload.score)
    return {"ok": True, "user": user["id"], "score": payload.score}

@fastapi_app.get("/api/leaderboard")
async def leaderboard_api():
    rows = get_leaderboard()
    return {
        "ok": True,
        "leaderboard": [
            {"user_id": uid, "name": name, "score": score}
            for uid, name, score in rows
        ],
    }
