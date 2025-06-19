import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests
import os
import json
from bs4 import BeautifulSoup
import re

# 🌱 Maak client_secret.json aan
if 'GOOGLE_CREDS' in os.environ:
    with open('client_secret.json', 'w') as f:
        f.write(os.environ['GOOGLE_CREDS'])

# 🔐 Auth Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
client = gspread.authorize(creds)
sheet = client.open("AI Spy Report")

# 📢 Telegram setup
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
def send_telegram_message(msg):
    if TELEGRAM_TOKEN and CHAT_ID:
        resp = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                             data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print("[Telegram]", resp.status_code, resp.text)

# 🆕 Worksheet met kolommen
def get_ws():
    title = "Week-" + datetime.now().strftime("%Y-W%U")
    try:
        return sheet.worksheet(title)
    except:
        ws = sheet.add_worksheet(title=title, rows="500", cols="20")
        headers = ["Datum","Productnaam","Prijs","Afbeelding","Productlink",
                   "Likes","Views","Shares","Reacties","Volgers","Engagement"]
        ws.append_row(headers)
        return ws

# 🎯 Scraping AliExpress met echte data (je past url & selectors nog aan naar jouw category)
def scrape_aliexpress():
    url = "https://www.aliexpress.com/category/100003109/women-clothing.html"
    h = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=h)
    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select("a._3t7zg")[:3]  # voorbeeldselector voor 3 items

    results = []
    for item in items:
        name = item.text.strip()
        link = item['href'] if item['href'].startswith('http') else "https:" + item['href']
        price = item.select_one("span._12A8D").text.strip() if item.select_one("span._12A8D") else ""
        img = item.select_one("img")['src'] if item.select_one("img") else ""
        results.append(dict(naam=name, prijs=price, link=link, image=img,
                            likes="", views="", shares="", reacties="", volgers=""))
    return results

# 🧪 Scraping TikTok trending via TikTok-alternatief
def scrape_tiktok_trending():
    # Hier is geen officiële TikTok-API beschikbaar, dus deze mocks simuleer ik realistisch
    return [
        dict(naam="LED Spiegeltje TikTok", prijs="29", link="https://www.tiktok.com/@account/video/123",
             image="https://via.placeholder.com/200", likes=23456, views=450000, shares=789, reacties=123, volgers=30000)
    ]

# 🛠 Run & append
def run():
    ws = get_ws()
    all_items = scrape_tiktok_trending() + scrape_aliexpress()
    for p in all_items:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        eng = round(int(p.get("likes",0)) / max(int(p.get("views",1)),1), 4) if p.get("views") else ""
        newrow = [now, p['naam'], p['prijs'], p['image'], p['link'],
                  p.get('likes',""), p.get('views',""), p.get('shares',""), p.get('reacties',""), p.get('volgers',""), eng]
        ws.append_row(newrow)
        send_telegram_message(f"*{p['naam']}* — {p['prijs']}\n👁 {p.get('views','')} views • ❤️ {p.get('likes','')} likes\n[Check product]({p['link']})")

if __name__ == "__main__":
    run()
