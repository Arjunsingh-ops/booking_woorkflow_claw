import json
import os

def find_alternative_slot(station_name: str, requested_slot: str = None, cross_station: bool = False) -> dict:
    """
    Purpose:
        Find alternative available slots when the preferred slot is taken.
        Can search at the same station or across all other stations.

    Input Schema:
        station_name (str): The name of the station that had the conflict.
        requested_slot (str, optional): The conflict slot (skipped during search).
        cross_station (bool, optional): If True, search across all OTHER stations instead of the current one.

    Output Schema:
        {
            "status": "FOUND" | "NONE_AVAILABLE" | "ERROR",
            "data": {
                "station": str | None,         # if same station, station name
                "slot": str | None,            # if same station, found slot
                "suggestions": list[dict],     # if cross_station, list of {"station": str, "slot": str}
                "checked_slots": list[str]     # list of slots checked during lookup for auditing
            } | None,
            "error": {
                "code": str,
                "message": str
            } | None
        }

    Failure Conditions:
        - station_name is empty or not a string.
        - stations.json or bookings.json is missing or corrupted.

    Escalation Conditions:
        - None (unresolved conflicts cause normal state transition to ESCALATE).
    """
    # Validation
    if not isinstance(station_name, str) or not station_name.strip():
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "INVALID_INPUT",
                "message": "Station name must be a non-empty string."
            }
        }

    stations_path = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")
    bookings_path = os.path.join(os.path.dirname(__file__), "..", "data", "bookings.json")

    # Load stations
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
                "message": f"Failed to parse stations database: {str(e)}"
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

    # Load bookings
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
                "message": f"Failed to parse bookings database: {str(e)}"
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

    # Map of booked slots per station (lowercased)
    booked_map = {}
    for b in bookings:
        stn = b.get("station", "").lower()
        sl = b.get("slot")
        if stn and sl:
            booked_map.setdefault(stn, set()).add(sl)

    checked_slots = []

    if not cross_station:
        # Strategy 1: Find next available slot at the same station
        target_station = None
        for s in stations:
            if s.get("name", "").lower() == station_name.strip().lower():
                target_station = s
                break

        if not target_station:
            return {
                "status": "ERROR",
                "data": None,
                "error": {
                    "code": "STATION_NOT_FOUND",
                    "message": f"Station '{station_name}' not found."
                }
            }

        slots = target_station.get("slots", [])
        stn_booked = booked_map.get(target_station.get("name", "").lower(), set())

        for slot in slots:
            checked_slots.append(slot)
            if requested_slot and slot == requested_slot:
                continue
            if slot not in stn_booked:
                return {
                    "status": "FOUND",
                    "data": {
                        "station": target_station.get("name"),
                        "slot": slot,
                        "suggestions": [],
                        "checked_slots": checked_slots
                    },
                    "error": None
                }

        return {
            "status": "NONE_AVAILABLE",
            "data": {
                "station": target_station.get("name"),
                "slot": None,
                "suggestions": [],
                "checked_slots": checked_slots
            },
            "error": None
        }

    else:
        # Strategy 2: Find all available slots across other stations
        suggestions = []
        for s in stations:
            s_name = s.get("name", "")
            if s_name.lower() == station_name.strip().lower():
                continue  # skip the original station
                
            slots = s.get("slots", [])
            stn_booked = booked_map.get(s_name.lower(), set())
            
            for slot in slots:
                checked_slots.append(f"{s_name}:{slot}")
                if slot not in stn_booked:
                    suggestions.append({
                        "station": s_name,
                        "slot": slot
                    })

        if suggestions:
            return {
                "status": "FOUND",
                "data": {
                    "station": None,
                    "slot": None,
                    "suggestions": suggestions,
                    "checked_slots": checked_slots
                },
                "error": None
            }

        return {
            "status": "NONE_AVAILABLE",
            "data": {
                "station": None,
                "slot": None,
                "suggestions": [],
                "checked_slots": checked_slots
            },
            "error": None
        }
