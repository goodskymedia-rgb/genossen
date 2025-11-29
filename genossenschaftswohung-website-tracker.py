import argparse
import hashlib
import json
import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
# === TELEGRAM CONFIGURATION ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Replace this with your actual token
if TELEGRAM_TOKEN is None:
    raise EnvironmentError("No TG Token Provided")
CHAT_IDS = ['5230902484']  # Replace with your Telegram user ID

# === APARTMENT SOURCES TO MONITOR ===
urls = {
    "Migra": "https://www.migra.at/immobilienangebot/wohnen/",
    "Wohnen.at": "https://www.wohnen.at/angebot/unser-wohnungsangebot/",
    "EBG": "https://www.ebg-wohnen.at/immobilien/wohnung",
    "EGW": "https://www.egw.at/suche",
    "OESW": "https://www.oesw.at/immobilienangebot/sofort-wohnen.html?financingType=2&rooms=3",
    "ÖVW": "https://www.oevw.at/suche",
    "WienSued": "https://www.wiensued.at/wohnen/?dev=&city=&search=&space-from=&space-to=&room-from=3&room-to=3&rent=1&state%5B%5D=sofort#search-results",
    "Heimbau": "https://www.heimbau.at/wiedervermietung",
    # "NHG": "https://www.nhg.at/immobilienangebot/wohnungsangebot/",
    "Geboes": "https://www.geboes.at/app/suche/ergebnisse?stocktype=Wohnung&state=Wien",
    "Sofort-Wohnen": "https://sofort-wohnen.at/wohnungen?keywordSearch=wien&ordering=-date_posted&owning=true&renting=true&subsidized=true&private=true&page=1&pageSize=10"
}

# === STORE PREVIOUS STATES ===
previous_hashes = {}



# === TELEGRAM MESSAGE FUNCTION ===
def send_telegram_message(message):
    for chat_id in CHAT_IDS:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {'chat_id': chat_id, 'text': message}
        response = requests.post(url, data=data)
        print(f"📨 Sent to {chat_id} → {response.status_code} | {response.text}")

# === FETCH AND HASH WEBSITE CONTENT ===
def get_content_hash(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text()
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"[ERROR] Could not fetch {url}: {e}")
        return None

with open("./state/hashes.json", "r") as input:
    current_hashes = json.loads(input.read())
    print("current_hashes", current_hashes)
#with open('./hashes.json', 'a') as output:
    #json.dump(get_content_hash(), output)



# === CHECK WEBSITES FOR CHANGES ===
def check_websites():
    for name, url in urls.items():
        current_hash = get_content_hash(url)
        if current_hash is None:
            continue

        if name in previous_hashes and previous_hashes[name] != current_hash:
            message = f"🔄 {name} has been updated!\n{url}"
            print(f"✅ Change detected: {name}")
            send_telegram_message(message)
        else:
            print(f"➖ No change: {name}")
            pass

        previous_hashes[name] = current_hash
    return previous_hashes

result = check_websites()
with open("./state/hashes.json", "w") as output:
    new_hashes = json.dumps(result)
    output.write(new_hashes)
    print("new_hashes=", new_hashes)

# === OPTIONAL: Notify that bot started ===

#send_telegram_message("🚀 Apartment bot is running and watching listings!")
