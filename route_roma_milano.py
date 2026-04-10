import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
ORS_API_KEY = os.environ["ORS_API_KEY"]

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()

def get_route():
    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [12.4964, 41.9028],  # Roma
            [9.1900, 45.4642]    # Milano
        ]
    }

    response = requests.post(url, json=body, headers=headers, timeout=30)

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    response.raise_for_status()
    return response.json()

def build_message(data):
    route = data["features"][0]
    summary = route["properties"]["summary"]

    duration_minutes = int(summary["duration"] / 60)
    distance_km = int(summary["distance"] / 1000)

    hours = duration_minutes // 60
    minutes = duration_minutes % 60

    text = (
        "🚗 Roma → Milano\n\n"
        f"Durata: {hours}h {minutes}m\n"
        f"Distanza: {distance_km} km"
    )

    return text

def main():
    data = get_route()
    text = build_message(data)
    send_telegram_message(text)

if __name__ == "__main__":
    main()
