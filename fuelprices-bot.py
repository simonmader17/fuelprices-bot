import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("TOKEN")
api = os.getenv("API")

# Commands
async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Processing /latest...")
    avanti = json.loads(requests.get(api + "/latestAvanti").text)
    jet = json.loads(requests.get(api + "/latestJet").text)
    jet_langenrohr = json.loads(requests.get(api + "/latestJetLangenrohr").text)
    bp = json.loads(requests.get(api + "/latestBp").text)
    text = f"""Avanti St. Pölten ({datetime.fromisoformat(avanti['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {avanti['avanti']} €
Jet St. Pölten ({datetime.fromisoformat(jet['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {jet['jet']} €
Jet Langenrohr ({datetime.fromisoformat(jet_langenrohr['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {jet_langenrohr['jetLangenrohr']} €
BP Böheimkirchen ({datetime.fromisoformat(bp['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {bp['bp']} €"""
    await update.message.reply_text(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Processing /help...")
    await update.message.reply_text(text="""*Commands*
/start \- Start receiving updates on new price lows
/stop \- Stop receiving updates on new price lows
/latest \- Show the latest fuel prices
/help \- Show command list""", parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Processing /start...")
    chat_id = update.effective_chat.id
    chat_ids = json.loads(requests.get(api + "/chatIDs").text)
    if chat_id in chat_ids:
        await update.message.reply_text("You are already receiving updates on new price lows and highs!")
    else:
        requests.post(api + "/chatIDs", json={"chatId": chat_id})
        await update.message.reply_text("You are now receiving updates on new price lows and highs.")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Processing /stop...")
    chat_id = update.effective_chat.id
    chat_ids = json.loads(requests.get(api + "/chatIDs").text)
    if chat_id in chat_ids:
        requests.delete(api + "/chatIDs", json={"chatId": chat_id})
        await update.message.reply_text("You are no longer receiving updates on new price lows and highs! Start again with /start")
    else:
        await update.message.reply_text("You haven't executed /start yet.")

# Messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received message: {update.message.text}")
    await update.message.reply_text("Enter a command. /help for more information.")

# main
if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("latest", latest_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stop", stop_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("Polling...")
    app.run_polling(poll_interval=3)
