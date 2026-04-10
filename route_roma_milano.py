import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
ORS_API_KEY = os.environ["ORS_API_KEY"]

ROMA = [12.4964, 41.9028]
MILANO = [9.1900, 45.4642]


def send_telegram_message(text: str):
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
        "coordinates": [ROMA, MILANO]
    }

    response = requests.post(url, json=body, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def format_duration(seconds: float) -> str:
    total_minutes = int(seconds // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h {minutes}m"


def format_distance(meters: float) -> str:
    return f"{int(meters // 1000)} km"


def clean_road_name(name: str) -> str:
    if not name:
        return ""
    name = name.strip()
    if name.lower() in {"unnamed road", "road", "-"}:
        return ""
    return name


def extract_main_roads(route: dict, max_roads: int = 5):
    roads = []

    for segment in route.get("segments", []):
        for step in segment.get("steps", []):
            road_name = clean_road_name(step.get("name", ""))

            # Se non c'è un nome strada utile, prova con l'istruzione
            if not road_name:
                instruction = step.get("instruction", "").strip()
                if instruction:
                    road_name = instruction

            if not road_name:
                continue

            # Evita ripetizioni consecutive
            if roads and roads[-1].lower() == road_name.lower():
                continue

            roads.append(road_name)

    # Riduci il rumore: tieni solo elementi "significativi"
    filtered = []
    seen = set()

    for road in roads:
        key = road.lower()
        looks_useful = any(token in road.upper() for token in ["A", "E", "SS", "SP", "SR", "TANGENZIALE"]) or len(road.split()) >= 2

        if not looks_useful:
            continue

        if key in seen:
            continue

        seen.add(key)
        filtered.append(road)

        if len(filtered) >= max_roads:
            break

    return filtered


def build_message(data: dict) -> str:
    route = data["routes"][0]
    summary = route["summary"]

    duration = format_duration(summary["duration"])
    distance = format_distance(summary["distance"])
    roads = extract_main_roads(route)

    lines = [
        "🚗 Roma → Milano",
        f"Durata stimata: {duration}",
        f"Distanza: {distance}",
        ""
    ]

    if roads:
        lines.append("Strada consigliata:")
        lines.append(" → ".join(roads))
    else:
        lines.append("Strada consigliata:")
        lines.append("Segui il percorso principale suggerito dall'API.")

    return "\n".join(lines)


def main():
    data = get_route()
    text = build_message(data)
    send_telegram_message(text)


if __name__ == "__main__":
    main()
