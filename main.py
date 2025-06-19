import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests
import pandas as pd
import os
import json
import random
from bs4 import BeautifulSoup
import re

# ➤ Schrijf service-account JSON uit env‑var
if 'GOOGLE_CREDS' in os.environ:
    with open('client_secret.json', 'w') as f:
        f.write(os.environ['GOOGLE_CREDS'])

# ➤ Google Sheets authenticatie
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
client = gspread.authorize(creds)
sheet = client.open("AI Spy Report")

# ➤ Telegram setup
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    resp = requests.post(url, data=data)
    print(f"[Telegram] {resp.status_code}: {resp.text}")

# ➤ Worksheet aanmaken met juiste kolommen
def get_or_create_worksheet():
    title = "Week-" + datetime.now().strftime("%Y-W%U")
    try: ws = sheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=title, rows="1000", cols="15")
        headers = ["Datum","Product","Prijs","Afbeelding","Productlink",
                   "Likes","Shares","Views","Reacties","Vol
