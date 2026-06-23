import json
import os

def check_slot(station_name, slot):
    """Check if a slot is available (not already booked) at a given station."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")
    bookings_path = os.path.join(os.path.dirname(__file__), "..", "data", "bookings.json")

    # First verify the slot exists for this station
    try:
        with open(data_path, "r") as f:
            stations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False

    station_found = None
    for station in stations:
        if station["name"].lower() == station_name.lower():
            station_found = station
            break

    if not station_found or slot not in station_found.get("slots", []):
        return False

    # Check if this slot is already booked
    try:
        with open(bookings_path, "r") as f:
            bookings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bookings = []

    for booking in bookings:
        if booking["station"].lower() == station_name.lower() and booking["slot"] == slot:
            return False

    return True
