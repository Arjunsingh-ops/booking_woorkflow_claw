import json
import os

def check_station(station_name):
    """Check if a station exists and return its data, or None if not found."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")

    try:
        with open(data_path, "r") as f:
            stations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    for station in stations:
        if station["name"].lower() == station_name.lower():
            return station

    return None
