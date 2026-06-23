import json
import os


def find_alternative_slot(station_name, requested_slot=None):
    """Return an alternative available slot for a station.

    Strategy:
    - Load station slots from data/stations.json
    - Load existing bookings from data/bookings.json
    - Return the first slot that is not booked (skipping requested_slot if provided)
    - Return None if no alternatives are available or station not found.
    """

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")
    bookings_path = os.path.join(os.path.dirname(__file__), "..", "data", "bookings.json")

    # Load station
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            stations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    station = None
    for s in stations:
        if s.get("name", "").lower() == station_name.lower():
            station = s
            break

    if not station:
        return None

    slots = station.get("slots", [])

    # Load bookings
    try:
        with open(bookings_path, "r", encoding="utf-8") as f:
            bookings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bookings = []

    booked = set()
    for b in bookings:
        if b.get("station", "").lower() == station_name.lower():
            booked.add(b.get("slot"))

    for slot in slots:
        if requested_slot is not None and slot == requested_slot:
            continue
        if slot not in booked:
            return slot

    return None

