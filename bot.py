import os
import json
import logging

from google.oauth2.service_account import Credentials
import gspread

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Environment variables (set these in Railway/Render, never hardcode) ----
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
GOOGLE_WORKSHEET_NAME = os.environ.get("GOOGLE_WORKSHEET_NAME", "Sheet1")
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]  # full JSON content of the service-account key, as one string

claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_sheet_data():
    """Read all rows from the moneyman output sheet (view-only)."""
    info = json.loads(GOOGLE_CREDENTIALS_JSON)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet(GOOGLE_WORKSHEET_NAME)
    return sheet.get_all_records()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "היי! אני הסוכן הפיננסי שלך. אפשר לשאול אותי כל שאלה על ההוצאות וההכנסות שלך."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    await update.message.chat.send_action("typing")

    try:
        transactions = get_sheet_data()
    except Exception:
        logger.exception("Failed reading sheet")
        await update.message.reply_text("לא הצלחתי לקרוא את הנתונים מהגיליון כרגע. נסה שוב עוד רגע.")
        return

    # keep the prompt small - only the most recent rows
    recent = transactions[-300:]

    system_prompt = (
        "אתה עוזר פיננסי אישי. יש לך גישה לרשימת תנועות בנקאיות של המשתמש "
        "(מצורפות כ-JSON). ענה בעברית, בקצרה ולעניין, אך ורק על סמך הנתונים שסופקו. "
        "אם משהו לא ברור מהנתונים - אמור זאת בפירוש ואל תמציא מספרים."
    )

    response = claude.messages.create(
        model="claude-sonnet-5",
        max_tokens=800,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"נתוני התנועות:\n{json.dumps(recent, ensure_ascii=False)}\n\nשאלה: {user_question}"}
        ],
    )

    answer = response.content[0].text
    await update.message.reply_text(answer)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot starting (polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()
