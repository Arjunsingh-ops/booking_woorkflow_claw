import json
import os

def get_booking_history(user: str) -> dict:
    """
    Purpose:
        Retrieve all booking records associated with a specific user.

    Input Schema:
        user (str): Name of the user whose booking history to retrieve.

    Output Schema:
        {
            "status": "SUCCESS" | "ERROR",
            "data": {
                "bookings": list[dict],
                "count": int
            } | None,
            "error": {
                "code": str,
                "message": str
            } | None
        }

    Failure Conditions:
        - user input is empty or not a string.
        - bookings.json is missing or corrupted.

    Escalation Conditions:
        - None.
    """
    # Validation
    if not isinstance(user, str) or not user.strip():
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "INVALID_INPUT",
                "message": "User must be a non-empty string."
            }
        }

    bookings_path = os.path.join(os.path.dirname(__file__), "..", "data", "bookings.json")

    try:
        if not os.path.exists(bookings_path):
            return {
                "status": "SUCCESS",
                "data": {
                    "bookings": [],
                    "count": 0
                },
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
    user_bookings = []

    for booking in bookings:
        if not isinstance(booking, dict):
            continue
        
        if booking.get("user", "").strip().lower() == user_lower:
            user_bookings.append(booking)

    return {
        "status": "SUCCESS",
        "data": {
            "bookings": user_bookings,
            "count": len(user_bookings)
        },
        "error": None
    }
