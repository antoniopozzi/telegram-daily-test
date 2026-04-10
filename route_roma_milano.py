import os
import re
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
    minutes = int(seconds // 60)
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours}h {minutes}m"


def format_distance(meters: float) -> str:
    return f"{int(meters // 1000)} km"


def normalize_label(text: str) -> str:
    text = text.upper().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def extract_road_refs(text: str):
    """
    Estrae riferimenti utili di alto livello:
    A1, A14, E35, SSxx, SPxx, TANGENZIALE, RACCORDO, VARIANTE...
    """
    if not text:
        return []

    t = normalize_label(text)
    found = []

    # Riferimenti stradali veri
    patterns = [
        r"\bA\d+\b",
        r"\bE\d+\b",
        r"\bSS\d+\b",
        r"\bSP\d+\b",
        r"\bSR\d+\b",
    ]

    for pattern in patterns:
        for match in re.findall(pattern, t):
            found.append(match)

    # Parole chiave macro
    keywords = [
        "TANGENZIALE",
        "RACCORDO",
        "VARIANTE DI VALICO",
        "VARIANTE",
        "AUTOSTRADA DEL SOLE",
    ]

    for keyword in keywords:
        if keyword in t:
            found.append(keyword)

    return found


def dedupe_keep_order(items):
    out = []
    seen = set()

    for item in items:
        key = item.strip().upper()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item.strip())

    return out


def extract_main_route(route: dict, max_items: int = 5):
    candidates = []

    for segment in route.get("segments", []):
        for step in segment.get("steps", []):
            name = step.get("name", "") or ""
            instruction = step.get("instruction", "") or ""

            # Cerca prima nel nome strada, poi nell'istruzione
            refs = extract_road_refs(name)
            refs += extract_road_refs(instruction)

            candidates.extend(refs)

    candidates = dedupe_keep_order(candidates)

    # Piccola pulizia: se abbiamo sia A1 che AUTOSTRADA DEL SOLE, teniamo entrambi solo se utili
    cleaned = []
    for item in candidates:
        if cleaned and cleaned[-1] == item:
            continue
        cleaned.append(item)

    return cleaned[:max_items]


def build_natural_sentence(roads):
    if not roads:
        return "Prendi il percorso principale suggerito dall'API fino a Milano."

    if len(roads) == 1:
        return f"Prendi {roads[0]} e prosegui fino a Milano."

    if len(roads) == 2:
        return f"Prendi {roads[0]}, poi {roads[1]} e prosegui fino a Milano."

    middle = ", poi ".join(roads[1:-1])
    return f"Prendi {roads[0]}, poi {middle}, poi {roads[-1]}."


def build_message(data: dict):
    route = data["routes"][0]
    summary = route["summary"]

    duration = format_duration(summary["duration"])
    distance = format_distance(summary["distance"])
    roads = extract_main_route(route)
    sentence = build_natural_sentence(roads)

    lines = [
        "🚗 Roma → Milano",
        f"Durata: {duration}",
        f"Distanza: {distance}",
        "",
        sentence
    ]

    if roads:
        lines += [
            "",
            "Riepilogo:",
            " → ".join(roads)
        ]

    return "\n".join(lines)


def main():
    data = get_route()
    message = build_message(data)
    send_telegram_message(message)


if __name__ == "__main__":
    main()
