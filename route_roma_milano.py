import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
ORS_API_KEY = os.environ["ORS_API_KEY"]

ROMA = [12.4964, 41.9028]
MILANO = [9.1900, 45.4642]


# --- TELEGRAM ---
def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()


# --- API ROUTE ---
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


# --- FORMAT ---
def format_duration(seconds: float) -> str:
    minutes = int(seconds // 60)
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours}h {minutes}m"


def format_distance(meters: float) -> str:
    return f"{int(meters // 1000)} km"


# --- LOGICA INTELLIGENTE ---
def extract_main_roads(route: dict):
    roads = []
    seen = set()

    for segment in route.get("segments", []):
        for step in segment.get("steps", []):
            name = step.get("name", "").upper()

            # Filtra SOLO roba importante
            if any(x in name for x in ["A", "E", "TANGENZIALE"]):
                clean = name.strip()

                if clean and clean not in seen:
                    seen.add(clean)
                    roads.append(clean)

    return roads[:5]  # massimo 5


def build_natural_sentence(roads):
    if not roads:
        return "Segui l'autostrada principale (A1) fino a Milano."

    if len(roads) == 1:
        return f"Prendi {roads[0]} e prosegui fino a destinazione."

    first = roads[0]
    rest = ", poi ".join(roads[1:])

    return f"Prendi {first}, poi {rest}."


# --- MESSAGGIO ---
def build_message(data: dict):
    route = data["routes"][0]
    summary = route["summary"]

    duration = format_duration(summary["duration"])
    distance = format_distance(summary["distance"])

    roads = extract_main_roads(route)
    sentence = build_natural_sentence(roads)

    return (
        "🚗 Roma → Milano\n\n"
        f"Durata: {duration}\n"
        f"Distanza: {distance}\n\n"
        f"{sentence}"
    )


# --- MAIN ---
def main():
    data = get_route()
    message = build_message(data)
    send_telegram_message(message)


if __name__ == "__main__":
    main()
