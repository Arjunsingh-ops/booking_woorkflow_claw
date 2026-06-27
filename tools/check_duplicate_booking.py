import json
import os

def check_duplicate_booking(user: str, station: str, slot: str) -> dict:
    """
    Purpose:
        Check if a user already has an active booking at the same station/slot to prevent duplicates.

    Input Schema:
        user (str): Name of the user booking.
        station (str): Name of the station.
        slot (str): Booked time slot.

    Output Schema:
        {
            "status": "DUPLICATE" | "NO_DUPLICATE" | "ERROR",
            "data": {
                "existing_booking": {
                    "booking_id": str,
                    "user": str,
                    "station": str,
                    "slot": str,
                    "booked_at": str
                } | None
            } | None,
            "error": {
                "code": str,
                "message": str
            } | None
        }

    Failure Conditions:
        - Input parameter missing or empty.
        - bookings.json is missing or corrupted.

    Escalation Conditions:
        - If duplicate is found, the workflow must transition to ESCALATE or handle gracefully.
    """
    # Validation
    if (not isinstance(user, str) or not user.strip() or 
        not isinstance(station, str) or not station.strip() or 
        not isinstance(slot, str) or not slot.strip()):
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "INVALID_INPUT",
                "message": "User, station, and slot must be non-empty strings."
            }
        }

    bookings_path = os.path.join(os.path.dirname(__file__), "..", "data", "bookings.json")

    try:
        if not os.path.exists(bookings_path):
            return {
                "status": "NO_DUPLICATE",
                "data": {"existing_booking": None},
                "error": None
            }

        with open(bookings_path, "r", encoding="utf-8") as f:
            bookings = json.load(f)
            
        if not isinstance(bookings, list):
            return {
                "status": "ERROR",
                "data": None,
                "error": {
                    "code": "CORRUPTED_JSON",
                    "message": "Bookings file contains invalid JSON structure."
                }
            }
    except json.JSONDecodeError as e:
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "JSON_DECODE_FAILED",
                "message": f"Failed to parse bookings: {str(e)}"
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

    user_lower = user.strip().lower()
    station_lower = station.strip().lower()
    slot_clean = slot.strip()

    for booking in bookings:
        if not isinstance(booking, dict):
            continue
        
        b_user = booking.get("user", "").strip().lower()
        b_station = booking.get("station", "").strip().lower()
        b_slot = booking.get("slot", "").strip()

        if b_user == user_lower and b_station == station_lower and b_slot == slot_clean:
            return {
                "status": "DUPLICATE",
                "data": {
                    "existing_booking": booking
                },
                "error": None
            }

    return {
        "status": "NO_DUPLICATE",
        "data": {
            "existing_booking": None
        },
        "error": None
    }
