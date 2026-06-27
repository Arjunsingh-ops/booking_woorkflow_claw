import json
import os

def check_slot(station_name: str, slot: str) -> dict:
    """
    Purpose:
        Verify if a specific time slot is valid and available (not already booked) at a station.

    Input Schema:
        station_name (str): The name of the station.
        slot (str): The time slot to check (e.g., "09:00").

    Output Schema:
        {
            "status": "AVAILABLE" | "UNAVAILABLE" | "INVALID_SLOT" | "ERROR",
            "data": {
                "station": str,
                "slot": str,
                "is_available": bool
            } | None,
            "error": {
                "code": str,
                "message": str
            } | None
        }

    Failure Conditions:
        - station_name or slot is empty, null, or not a string.
        - stations.json or bookings.json is missing or corrupted.

    Escalation Conditions:
        - None (slot unavailability transitions to alternative slot searching).
    """
    # Input validation
    if not isinstance(station_name, str) or not station_name.strip() or not isinstance(slot, str) or not slot.strip():
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "INVALID_INPUT",
                "message": "Both station_name and slot must be non-empty strings."
            }
        }

    stations_path = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")
    bookings_path = os.path.join(os.path.dirname(__file__), "..", "data", "bookings.json")

    # 1. Verify the station exists and has the requested slot
    try:
        if not os.path.exists(stations_path):
            return {
                "status": "ERROR",
                "data": None,
                "error": {
                    "code": "FILE_NOT_FOUND",
                    "message": "Stations database file not found."
                }
            }
            
        with open(stations_path, "r", encoding="utf-8") as f:
            stations = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "JSON_DECODE_FAILED",
                "message": f"Failed to parse stations JSON: {str(e)}"
            }
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "UNEXPECTED_ERROR",
                "message": str(e)
            }
        }

    station_found = None
    for s in stations:
        if s.get("name", "").lower() == station_name.strip().lower():
            station_found = s
            break

    if not station_found:
        return {
            "status": "INVALID_SLOT",
            "data": None,
            "error": {
                "code": "STATION_NOT_FOUND",
                "message": f"Station '{station_name}' not found."
            }
        }

    if slot not in station_found.get("slots", []):
        return {
            "status": "INVALID_SLOT",
            "data": None,
            "error": {
                "code": "INVALID_SLOT_FOR_STATION",
                "message": f"Slot '{slot}' is not a valid operating hour for station '{station_found.get('name')}'."
            }
        }

    # 2. Check if this slot is already booked
    try:
        if not os.path.exists(bookings_path):
            bookings = []
        else:
            with open(bookings_path, "r", encoding="utf-8") as f:
                bookings = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "JSON_DECODE_FAILED",
                "message": f"Failed to parse bookings JSON: {str(e)}"
            }
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "UNEXPECTED_ERROR",
                "message": str(e)
            }
        }

    for booking in bookings:
        if (booking.get("station", "").lower() == station_name.strip().lower() and 
            booking.get("slot") == slot):
            return {
                "status": "UNAVAILABLE",
                "data": {
                    "station": station_found.get("name"),
                    "slot": slot,
                    "is_available": False
                },
                "error": None
            }

    return {
        "status": "AVAILABLE",
        "data": {
            "station": station_found.get("name"),
            "slot": slot,
            "is_available": True
        },
        "error": None
    }
