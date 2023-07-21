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
    res_avanti = requests.get(api + "/latestAvanti")
    res_jet = requests.get(api + "/latestJet")
    avanti = json.loads(res_avanti.text)
    jet = json.loads(res_jet.text)
    text = f"""Avanti ({datetime.fromisoformat(avanti['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {avanti['avanti']} €
Jet ({datetime.fromisoformat(jet['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {jet['jet']} €"""
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
    # jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    # if jobs:
    #     await update.message.reply_text("You are already receiving updates on new price lows!")
    # else:
    #     wait_minutes = timedelta(minutes=61 - datetime.now().minute)
    #     context.job_queue.run_repeating(check_new_low, interval=3600, first=wait_minutes, chat_id=chat_id, name=str(chat_id))
    #     await update.message.reply_text("You are now receiving updates on new price lows.")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Processing /stop...")
    chat_id = update.effective_chat.id
    chat_ids = json.loads(requests.get(api + "/chatIDs").text)
    if chat_id in chat_ids:
        requests.delete(api + "/chatIDs", json={"chatId": chat_id})
        await update.message.reply_text("You are no longer receiving updates on new price lows and highs! Start again with /start")
    else:
        await update.message.reply_text("You haven't executed /start yet.")
    # job = context.job_queue.get_jobs_by_name(str(chat_id))[0]
    # job.schedule_removal()
    # await update.message.reply_text("You are no longer receiving update on new price lows! Start again with /start")

# async def check_new_low(context: ContextTypes.DEFAULT_TYPE):
#     print("Checking for new lows...")

#     text = []
#     avanti = json.loads(requests.get(api + "/latestAvanti").text)
#     low_month_avanti = json.loads(requests.get(api + "/lowestAvantiMonth").text)
#     if avanti["avanti"] < low_month_avanti:
#         # New avanti monthly low
#         text.append(f"""❗❗❗New monthly low for avanti❗❗❗
# Avanti ({datetime.fromisoformat(avanti['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {avanti['avanti']} €""")
#     else:
#         low_week_avanti = json.loads(requests.get(api + "/lowestAvantiWeek").text)
#         if avanti["avanti"] < low_week_avanti:
#             # New avanti weekly low
#             text.append(f"""❗New weekly low for avanti❗
# Avanti ({datetime.fromisoformat(avanti['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {avanti['avanti']} €""")
#     jet = json.loads(requests.get(api + "/latestJet").text)
#     low_month_jet = json.loads(requests.get(api + "/lowestJetMonth").text)
#     if jet["jet"] < low_month_jet:
#         # New jet monthly low
#         text.append(f"""❗❗❗New monthly low for jet❗❗❗
# Jet ({datetime.fromisoformat(jet['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {jet['jet']} €""")
#     else:
#         low_week_jet = json.loads(requests.get(api + "/lowestJetWeek").text)
#         if jet["jet"] < low_week_jet:
#             # New jet weekly low
#             text.append(f"""❗New weekly low for jet❗
# Jet ({datetime.fromisoformat(jet['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {jet['jet']} €""")

#     if len(text) > 0:
#         job = context.job
#         chat_id = job.chat_id
#         await context.bot.send_message(chat_id, text="\n".join(text))

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
