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

async def check_new_low():
    print("Checking for new lows...")

    text = []
    avanti = json.loads(requests.get(api + "/latestAvanti").text)
    low_month_avanti = json.loads(requests.get(api + "/lowestAvantiMonth").text)
    if avanti["avanti"] < low_month_avanti:
        # New avanti monthly low
        text.append(f"""🟩🟩🟩New monthly low for avanti🟩🟩🟩
Avanti ({datetime.fromisoformat(avanti['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {avanti['avanti']} €""")
    else:
        low_week_avanti = json.loads(requests.get(api + "/lowestAvantiWeek").text)
        if avanti["avanti"] < low_week_avanti:
            # New avanti weekly low
            text.append(f"""🟩New weekly low for avanti🟩
Avanti ({datetime.fromisoformat(avanti['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {avanti['avanti']} €""")
    jet = json.loads(requests.get(api + "/latestJet").text)
    low_month_jet = json.loads(requests.get(api + "/lowestJetMonth").text)
    if jet["jet"] < low_month_jet:
        # New jet monthly low
        text.append(f"""🟩🟩🟩New monthly low for jet🟩🟩🟩
Jet ({datetime.fromisoformat(jet['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {jet['jet']} €""")
    else:
        low_week_jet = json.loads(requests.get(api + "/lowestJetWeek").text)
        if jet["jet"] < low_week_jet:
            # New jet weekly low
            text.append(f"""🟩New weekly low for jet🟩
Jet ({datetime.fromisoformat(jet['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {jet['jet']} €""")

    if len(text) > 0:
        chat_ids = json.loads(requests.get(api + "/chatIDs").text)
        for chat_id in chat_ids:
            await bot.send_message(chat_id=chat_id, text="\n".join(text))

async def check_new_high():
    print("Checking for new highs...")

    text = []
    avanti = json.loads(requests.get(api + "/latestAvanti").text)
    high_month_avanti = json.loads(requests.get(api + "/highestAvantiMonth").text)
    if avanti["avanti"] > high_month_avanti:
        # New avanti monthly high
        text.append(f"""🟥🟥🟥New monthly high for avanti🟥🟥🟥
Avanti ({datetime.fromisoformat(avanti['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {avanti['avanti']} €""")
    else:
        high_week_avanti = json.loads(requests.get(api + "/highestAvantiWeek").text)
        if avanti["avanti"] > high_week_avanti:
            # New avanti weekly high
            text.append(f"""🟥New weekly high for avanti🟥
Avanti ({datetime.fromisoformat(avanti['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {avanti['avanti']} €""")
    jet = json.loads(requests.get(api + "/latestJet").text)
    high_month_jet = json.loads(requests.get(api + "/highestJetMonth").text)
    if jet["jet"] > high_month_jet:
        # New jet monthly high
        text.append(f"""🟥🟥🟥New monthly high for jet🟥🟥🟥
Jet ({datetime.fromisoformat(jet['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {jet['jet']} €""")
    else:
        high_week_jet = json.loads(requests.get(api + "/highestJetWeek").text)
        if jet["jet"] > high_week_jet:
            # New jet weekly high
            text.append(f"""🟥New weekly high for jet🟥
Jet ({datetime.fromisoformat(jet['timestamp']).astimezone().strftime('%d.%m.%y, %H:%M')}): {jet['jet']} €""")

    if len(text) > 0:
        chat_ids = json.loads(requests.get(api + "/chatIDs").text)
        for chat_id in chat_ids:
            await bot.send_message(chat_id=chat_id, text="\n".join(text))

async def main():
    await check_new_low()
    await check_new_high()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())