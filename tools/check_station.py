import json
import os

def check_station(station_name: str) -> dict:
    """
    Purpose:
        Verify if an EV charging station exists in the database.

    Input Schema:
        station_name (str): The name of the station to check (case-insensitive).

    Output Schema:
        {
            "status": "SUCCESS" | "NOT_FOUND" | "ERROR",
            "data": {
                "name": str,
                "location": str,
                "slots": list[str]
            } | None,
            "error": {
                "code": str,
                "message": str
            } | None
        }

    Failure Conditions:
        - station_name is empty, null, or not a string.
        - stations.json file is missing or contains invalid JSON structure.

    Escalation Conditions:
        - None (station existence is a simple database lookup; invalid stations cause state machine transition to ESCALATE).
    """
    # Input validation
    if not isinstance(station_name, str) or not station_name.strip():
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "INVALID_INPUT",
                "message": "Station name must be a non-empty string."
            }
        }

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")

    try:
        if not os.path.exists(data_path):
            return {
                "status": "ERROR",
                "data": None,
                "error": {
                    "code": "FILE_NOT_FOUND",
                    "message": f"Stations database file not found at {data_path}."
                }
            }

        with open(data_path, "r", encoding="utf-8") as f:
            stations = json.load(f)
            
        if not isinstance(stations, list):
            return {
                "status": "ERROR",
                "data": None,
                "error": {
                    "code": "CORRUPTED_JSON",
                    "message": "Stations file is not a valid list."
                }
            }
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

    for station in stations:
        if isinstance(station, dict) and station.get("name", "").lower() == station_name.strip().lower():
            return {
                "status": "SUCCESS",
                "data": {
                    "name": station.get("name"),
                    "location": station.get("location"),
                    "slots": station.get("slots", [])
                },
                "error": None
            }

    return {
        "status": "NOT_FOUND",
        "data": None,
        "error": {
            "code": "STATION_NOT_FOUND",
            "message": f"Station '{station_name}' does not exist."
        }
    }
