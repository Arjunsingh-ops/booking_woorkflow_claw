import json
import os
from datetime import datetime

def create_booking(user, station, slot):
    bookings_path = os.path.join(os.path.dirname(__file__), "..", "data", "bookings.json")

    try:
        with open(bookings_path, "r", encoding="utf-8") as f:
            bookings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bookings = []

    bookings.append({
        "user": user,
        "station": station,
        "slot": slot,
        "booked_at": datetime.now().isoformat()
    })

    with open(bookings_path, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2)

    return "Booking Confirmed"