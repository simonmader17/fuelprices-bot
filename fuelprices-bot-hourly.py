import requests
import json
import datetime
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()
TOKEN = os.getenv("TOKEN")
api = os.getenv("API")
bot = Bot(token=TOKEN)

# latest = json.loads(requests.get(api + "/latest").text)
lowest_week = json.loads(requests.get(api + "/lowestSinceDays?days=7").text)
lowest_month = json.loads(requests.get(api + "/lowestSinceDays?days=30").text)
highest_week = json.loads(requests.get(api + "/highestSinceDays?days=7").text)
highest_month = json.loads(requests.get(api + "/highestSinceDays?days=30").text)

gas_stations = ["jet", "avanti", "jetLangenrohr", "bp"]

async def check_new_low():
    print("Checking for new lows...")

    text = []
    for station in gas_stations:
        station_latest = json.loads(requests.get(api + f"/latest{station[0].upper() + station[1:]}").text)
        station_before_latest = json.loads(requests.get(api + f"/latest{station[0].upper() + station[1:]}?i=1").text)
        if station_latest[station] == station_before_latest[station]:
            continue;
        elif station_latest[station] <= lowest_month[station]:
            # New monthly low
            text.append(f"""🟩🟩🟩New monthly low for {station.upper()}🟩🟩🟩
{station.upper()} ({datetime.fromisoformat(station_latest['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {station_latest[station]} €""")
        elif station_latest[station] <= lowest_week[station]:
            text.append(f"""🟩New weekly low for {station.upper()}🟩
{station.upper()} ({datetime.fromisoformat(station_latest['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {station_latest[station]} €""")

    if len(text) > 0:
        message_text = "\n".join(text)
        print(message_text)
        chat_ids = json.loads(requests.get(api + "/chatIDs").text)
        for chat_id in chat_ids:
            await bot.send_message(chat_id=chat_id, text=message_text)

async def check_new_high():
    print("Checking for new highs...")

    text = []
    for station in gas_stations:
        station_latest = json.loads(requests.get(api + f"/latest{station[0].upper() + station[1:]}").text)
        station_before_latest = json.loads(requests.get(api + f"/latest{station[0].upper() + station[1:]}?i=1").text)
        if station_latest[station] == station_before_latest[station]:
            continue;
        elif station_latest[station] >= highest_month[station]:
            # New monthly low
            text.append(f"""🟥🟥🟥New monthly high for {station.upper()}🟥🟥🟥
{station.upper()} ({datetime.fromisoformat(station_latest['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {station_latest[station]} €""")
        elif station_latest[station] >= highest_week[station]:
            text.append(f"""🟥New weekly high for {station.upper()}🟥
{station.upper()} ({datetime.fromisoformat(station_latest['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {station_latest[station]} €""")

    if len(text) > 0:
        message_text = "\n".join(text)
        print(message_text)
        chat_ids = json.loads(requests.get(api + "/chatIDs").text)
        for chat_id in chat_ids:
            await bot.send_message(chat_id=chat_id, text=message_text)

async def main():
    await check_new_low()
    await check_new_high()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())