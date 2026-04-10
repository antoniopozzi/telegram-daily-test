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
        ],
        "alternative_routes": {
            "target_count": 3,
            "weight_factor": 1.4
        }
    }

    response = requests.post(url, json=body, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()

def format_route(route):
    summary = route["properties"]["summary"]
    duration_minutes = int(summary["duration"] / 60)
    distance_km = int(summary["distance"] / 1000)

    hours = duration_minutes // 60
    minutes = duration_minutes % 60

    return f"{hours}h {minutes}m", f"{distance_km} km"

def build_message(data):
    routes = data["features"]
    best = routes[0]
    duration, distance = format_route(best)

    lines = [
        "🚗 Roma → Milano",
        "",
        f"Percorso principale: {duration}",
        f"Distanza: {distance}"
    ]

    if len(routes) > 1:
        lines.append("")
        lines.append("Alternative:")
        for i, route in enumerate(routes[1:], start=1):
            alt_duration, alt_distance = format_route(route)
            lines.append(f"- Alt {i}: {alt_duration}, {alt_distance}")

    return "\n".join(lines)

def main():
    data = get_route()
    text = build_message(data)
    send_telegram_message(text)

if __name__ == "__main__":
    main()