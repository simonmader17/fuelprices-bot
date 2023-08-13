import requests
import json
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv
import telegram
from telegram import Bot
import logging
logging.basicConfig(
    format='%(asctime)s [ %(levelname)-8s ] %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)

load_dotenv()
TOKEN = os.getenv("TOKEN")
api = os.getenv("API")
bot = Bot(token=TOKEN)

logging.info("""
=======================================
Starting new price lows and highs check
=======================================""")

# latest = json.loads(requests.get(api + "/latest").text)
lowest_week = json.loads(requests.get(api + "/lowestSinceDays?days=7").text)
lowest_month = json.loads(requests.get(api + "/lowestSinceDays?days=30").text)
highest_week = json.loads(requests.get(api + "/highestSinceDays?days=7").text)
highest_month = json.loads(requests.get(api + "/highestSinceDays?days=30").text)

gas_stations = {"jet": "Jet St. Pölten", "avanti": "Avanti St. Pölten", "jetLangenrohr": "Jet Langenrohr", "bp": "BP Böheimkirchen"}

async def check_new_low():
    logging.info("Checking for new lows...")

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
        latest = json.loads(requests.get(api + "/latest").text)
        logging.error(latest)

    if len(text) > 0:
        message_text = "\n".join(text)
        message_text = message_text.replace(".", "\.")
        if monthly:
            message_text = f"🟩🟩🟩\n{message_text}\n🟩🟩🟩"
        else:
            message_text = f"🟩\n{message_text}\n🟩"
        logging.info(message_text)
        chat_ids = json.loads(requests.get(api + "/chatIDs").text)
        for chat_id in chat_ids:
            await bot.send_message(chat_id=chat_id, text=message_text, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

async def check_new_high():
    logging.info("Checking for new highs...")

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
        latest = json.loads(requests.get(api + "/latest").text)
        logging.error(latest)

    if len(text) > 0:
        message_text = "\n".join(text)
        message_text = message_text.replace(".", "\.")
        if monthly:
            message_text = f"🟥🟥🟥\n{message_text}\n🟥🟥🟥"
        else:
            message_text = f"🟥\n{message_text}\n🟥"
        logging.info(message_text)
        chat_ids = json.loads(requests.get(api + "/chatIDs").text)
        for chat_id in chat_ids:
            await bot.send_message(chat_id=chat_id, text=message_text, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

async def main():
    await check_new_low()
    await check_new_high()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
