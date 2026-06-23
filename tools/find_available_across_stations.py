import json
import os


def find_available_across_stations(exclude_station=None):
    """Return a list of {station, slot} pairs that are available across ALL stations.

    Args:
        exclude_station: Optionally skip this station (the one already tried).

    Returns:
        List of dicts: [{"station": "Station B", "slot": "11:00"}, ...]
    """
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")
    bookings_path = os.path.join(os.path.dirname(__file__), "..", "data", "bookings.json")

    # Load all stations
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            stations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    # Load all bookings
    try:
        with open(bookings_path, "r", encoding="utf-8") as f:
            bookings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bookings = []

    # Build a set of (station_lower, slot) that are already booked
    booked = set()
    for b in bookings:
        booked.add((b.get("station", "").lower(), b.get("slot")))

    suggestions = []
    for station in stations:
        name = station.get("name", "")
        if exclude_station and name.lower() == exclude_station.lower():
            continue
        for slot in station.get("slots", []):
            if (name.lower(), slot) not in booked:
                suggestions.append({"station": name, "slot": slot})

    return suggestions
