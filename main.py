import os
import requests
from datetime import datetime, timezone

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    text = f"Routine OK\nEsecuzione automatica riuscita\nOra: {now}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    print(response.json())

if __name__ == "__main__":
    send_message()