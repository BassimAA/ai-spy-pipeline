name: ai-spy-pipeline

on:
  schedule:
    - cron: '0 7 * * 1'   # ma 07:00 UTC = 09:00 NL
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run AI‑Spy
        env:
          GOOGLE_CREDS: ${{ secrets.GOOGLE_CREDS }}
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          CHAT_ID: ${{ secrets.CHAT_ID }}
        run: python main.py

Verbeterde main.py: met foto's, links, KPI's & Telegram fix
