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

# ✅ Auth setup from environment variable
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
with open("client_secret.json", "w") as f:
    json.dump(creds_dict, f)

creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
client = gspread.authorize(creds)
sheet = client.open("AI Spy Report")

# ✅ Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def get_or_create_worksheet(date_type='weekly'):
    if date_type == 'weekly':
        title = "Week-" + datetime.now().strftime("%Y-W%U")
    else:
        title = datetime.now().strftime("%Y-%m-%d")
    try:
        worksheet = sheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=title, rows="1000", cols="10")
        worksheet.append_row(["Datum", "Product", "Prijs", "URL"])
    return worksheet

def log_product(product, price, url, date_type='weekly'):
    datum = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    worksheet = get_or_create_worksheet(date_type)
    worksheet.append_row([datum, product, price, url])
    msg = f"🛒 Nieuw product:\n📌 {product}\n💰 €{price}\n🔗 {url}"
    send_telegram_message(msg)

def scrape_aliexpress_products():
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.aliexpress.com/category/100003109/women-clothing.html"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    titles = [tag.text.strip() for tag in soup.find_all("a", attrs={"class": re.compile(".*item-title.*")})][:1]
    links = [tag["href"] for tag in soup.find_all("a", href=True) if "item" in tag["href"]][:1]
    prices = [str(random.randint(10, 60)) for _ in titles]
    return list(zip(titles, prices, links))

def scrape_tiktok_trending():
    producten = [
        ("Viral LED Spiegel", "35", "https://tiktok.com/example1"),
        ("Zelfroerende Mok", "28", "https://tiktok.com/example2"),
    ]
    return producten

def analyse_trending(week_title):
    try:
        ws = sheet.worksheet(week_title)
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            return "Geen data"
        trend = df["Product"].value_counts().head(3)
        result = "\n📈 Trending producten deze week:\n"
        for item, count in trend.items():
            result += f"• {item} – {count}x\n"
        send_telegram_message(result)
        return result
    except:
        return "Worksheet niet gevonden."

def run_full_weekly_spy():
    for product, price, url in scrape_aliexpress_products():
        log_product(product, price, url, date_type="weekly")
    for product, price, url in scrape_tiktok_trending():
        log_product(product, price, url, date_type="weekly")
    week_title = "Week-" + datetime.now().strftime("%Y-W%U")
    analyse_trending(week_title)

if __name__ == "__main__":
    run_full_weekly_spy()
