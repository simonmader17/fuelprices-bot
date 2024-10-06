import requests
import json
import os
from datetime import datetime, timedelta, timezone

import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

TOKEN = os.getenv("TOKEN")
api = "http://fuelprices-api:30011"

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

# Hourly checks
async def check_new_low(context: ContextTypes.DEFAULT_TYPE):
    print("Checking for new lows...")

    lowest_week = json.loads(requests.get(api + "/lowestSinceDays?days=7").text)
    lowest_month = json.loads(requests.get(api + "/lowestSinceDays?days=30").text)

    gas_stations = {"jet": "Jet St. Pölten", "avanti": "Avanti St. Pölten", "jetLangenrohr": "Jet Langenrohr", "bp": "BP Böheimkirchen"}

    text = []
    monthly = False
    for station, label in gas_stations.items():
        station_latest = json.loads(requests.get(api + f"/latest{station[0].upper() + station[1:]}").text)
        station_before_latest = json.loads(requests.get(api + f"/latest{station[0].upper() + station[1:]}?i=1").text)
        if station_latest[station] == station_before_latest[station]:
            continue;
        elif station_latest[station] <= lowest_month[station]:
            # New monthly low
            monthly = True
            text.append(f"""*New monthly low for {label}*
{label} \({datetime.fromisoformat(station_latest['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}\): {str(station_latest[station]).replace(".", ",")} €""")
        elif station_latest[station] <= lowest_week[station]:
            # New weekly low
            text.append(f"""*New weekly low for {label}*
{label} \({datetime.fromisoformat(station_latest['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}\): {str(station_latest[station]).replace(".", ",")} €""")

    if len(text) == 0:
        print("No new lows!")
        # latest = json.loads(requests.get(api + "/latest").text)
        # logging.error(latest)

    if len(text) > 0:
        message_text = "\n".join(text)
        message_text = message_text.replace(".", "\.")
        if monthly:
            message_text = f"🟩🟩🟩\n{message_text}\n🟩🟩🟩"
        else:
            message_text = f"🟩\n{message_text}\n🟩"
        # logging.info(message_text)
        print(message_text)
        chat_ids = json.loads(requests.get(api + "/chatIDs").text)
        for chat_id in chat_ids:
            print(f"Sending notification to {chat_id}...")
            try:
                await context.bot.send_message(chat_id=chat_id, text=message_text, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
            except TelegramError as e:
                print(f"Could not send notification to {chat_id}: " + str(e))

async def check_new_high(context: ContextTypes.DEFAULT_TYPE):
    print("Checking for new highs...")

    highest_week = json.loads(requests.get(api + "/highestSinceDays?days=7").text)
    highest_month = json.loads(requests.get(api + "/highestSinceDays?days=30").text)

    gas_stations = {"jet": "Jet St. Pölten", "avanti": "Avanti St. Pölten", "jetLangenrohr": "Jet Langenrohr", "bp": "BP Böheimkirchen"}

    text = []
    monthly = False
    for station, label in gas_stations.items():
        station_latest = json.loads(requests.get(api + f"/latest{station[0].upper() + station[1:]}").text)
        station_before_latest = json.loads(requests.get(api + f"/latest{station[0].upper() + station[1:]}?i=1").text)
        if station_latest[station] == station_before_latest[station]:
            continue;
        elif station_latest[station] >= highest_month[station]:
            # New monthly high
            monthly = True
            text.append(f"""*New monthly high for {label}*
{label} \({datetime.fromisoformat(station_latest['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}\): {str(station_latest[station]).replace(".", ",")} €""")
        elif station_latest[station] >= highest_week[station]:
            # New weekly high
            text.append(f"""*New weekly high for {label}*
{label} \({datetime.fromisoformat(station_latest['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}\): {str(station_latest[station]).replace(".", ",")} €""")

    if len(text) == 0:
        print("No new highs!")
        # latest = json.loads(requests.get(api + "/latest").text)
        # logging.error(latest)

    if len(text) > 0:
        message_text = "\n".join(text)
        message_text = message_text.replace(".", "\.")
        if monthly:
            message_text = f"🟥🟥🟥\n{message_text}\n🟥🟥🟥"
        else:
            message_text = f"🟥\n{message_text}\n🟥"
        # logging.info(message_text)
        print(message_text)
        chat_ids = json.loads(requests.get(api + "/chatIDs").text)
        for chat_id in chat_ids:
            print(f"Sending notification to {chat_id}...")
            try:
                await context.bot.send_message(chat_id=chat_id, text=message_text, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
            except TelegramError as e:
                print(f"Could not send notification to {chat_id}: " + str(e))

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

    # Hourly checks
    now = datetime.now(timezone.utc)
    if now.minute > 0 or now.second > 0 or now.microsecond > 0:
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        next_hour = now
    app.job_queue.run_repeating(check_new_low, interval=timedelta(hours=1), first=next_hour)
    app.job_queue.run_repeating(check_new_high, interval=timedelta(hours=1), first=next_hour)

    print("Polling...")
    app.run_polling()
