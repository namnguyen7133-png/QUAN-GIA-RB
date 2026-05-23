import requests
from datetime import datetime

# Doc token tu file
def doc_token(duong_dan):
    try:
        with open(duong_dan, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return None

SLACK_URL = doc_token("D:/APP SCRIPT/SLACK_WEBHOOK_URL.txt")
PUSHBULLET_TOKEN = doc_token("D:/APP SCRIPT/PUSHBULLET_TOKEN.txt")

# Gui thong bao test
print(f"=== Test gui thong bao luc {datetime.now().strftime('%H:%M')} ===")

noi_dung = """
✅ DA SUA LOI THANH CONG!

Loi: no such column: temperature_2m_min
File: locdlvaduasheet.py
Dong: 194
Database: D:/CASHFLOW/data/weather.db

Da them cot temperature_2m_min vao database.
"""

# Thu gui Slack
if SLACK_URL:
    try:
        r = requests.post(SLACK_URL, json={"text": noi_dung})
        print(f"Slack: {r.status_code}")
    except Exception as e:
        print(f"Slack loi: {e}")

# Thu gui Pushbullet
if PUSHBULLET_TOKEN:
    try:
        r = requests.post(
            "https://api.pushbullet.com/v2/pushes",
            json={"type": "note", "title": "SUA LOI THANH CONG", "body": noi_dung},
            headers={"Access-Token": PUSHBULLET_TOKEN}
        )
        print(f"Pushbullet: {r.status_code}")
    except Exception as e:
        print(f"Pushbullet loi: {e}")