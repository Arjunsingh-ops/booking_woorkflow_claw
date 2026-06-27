import json
import os
import uuid
from datetime import datetime

def create_booking(user: str, station: str, slot: str) -> dict:
    """
    Purpose:
        Create a booking record and write it to the bookings database.

    Input Schema:
        user (str): Name of the user booking.
        station (str): Station name.
        slot (str): Booked time slot.

    Output Schema:
        {
            "status": "SUCCESS" | "ERROR",
            "data": {
                "booking_id": str,
                "user": str,
                "station": str,
                "slot": str,
                "booked_at": str
            } | None,
            "error": {
                "code": str,
                "message": str
            } | None
        }

    Failure Conditions:
        - Input parameter missing or empty.
        - bookings.json is missing or corrupted.
        - File write permission errors.

    Escalation Conditions:
        - If file writing fails, escalate as CRITICAL tool execution failure.
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
        # Load existing bookings
        if not os.path.exists(bookings_path):
            bookings = []
        else:
            with open(bookings_path, "r", encoding="utf-8") as f:
                bookings = json.load(f)
                
            if not isinstance(bookings, list):
                bookings = []
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
                "code": "LOAD_ERROR",
                "message": f"Unexpected error loading bookings database: {str(e)}"
            }
        }

    booking_id = str(uuid.uuid4())
    booked_at = datetime.now().isoformat()

    new_booking = {
        "booking_id": booking_id,
        "user": user.strip(),
        "station": station.strip(),
        "slot": slot.strip(),
        "booked_at": booked_at
    }

    bookings.append(new_booking)

    # Persist
    try:
        os.makedirs(os.path.dirname(bookings_path), exist_ok=True)
        with open(bookings_path, "w", encoding="utf-8") as f:
            json.dump(bookings, f, indent=2)
    except IOError as e:
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "WRITE_FAILURE",
                "message": f"Failed to write booking to disk: {str(e)}"
            }
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "UNEXPECTED_ERROR",
                "message": f"Unexpected error during booking persistence: {str(e)}"
            }
        }

    return {
        "status": "SUCCESS",
        "data": new_booking,
        "error": None
    }