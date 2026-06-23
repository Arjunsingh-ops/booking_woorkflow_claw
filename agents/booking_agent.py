from tools.check_station import check_station
from tools.check_slot import check_slot
from tools.find_alternative_slot import find_alternative_slot
from tools.create_booking import create_booking
from tools.generate_log import generate_log
from tools.escalate_issue import escalate_issue
from tools.find_available_across_stations import find_available_across_stations


def booking_agent(user, station, slot, auto_rebook=True):
    station_data = check_station(station)

    if not station_data:
        return {
            "debug": "station_not_found",
            "station": station,
        }

    available = check_slot(station, slot)

    # Requested slot is available: confirm booking
    if available:
        create_booking(user, station, slot)
        return {
            "debug": "slot_available",
            "status": "CONFIRMED",
            "station": station,
            "slot": slot,
            "log": generate_log(user, station, slot),
        }

    # Requested slot is not available: try alternative
    alternative = find_alternative_slot(station, slot)

    if alternative is not None:
        create_booking(user, station, alternative)
        return {
            "debug": "slot_unavailable",
            "status": "CONFIRMED_ALTERNATIVE",
            "requested_slot": slot,
            "station": station,
            "slot": alternative,
            "log": generate_log(user, station, alternative),
        }

    # No alternatives exist at this station: suggest slots across all other stations
    suggestions = find_available_across_stations(exclude_station=station)

    if auto_rebook and suggestions:
        rebooked_station = suggestions[0]["station"]
        rebooked_slot = suggestions[0]["slot"]
        create_booking(user, rebooked_station, rebooked_slot)
        return {
            "debug": "auto_rebooked",
            "status": "AUTO_REBOOKED",
            "requested_station": station,
            "requested_slot": slot,
            "station": rebooked_station,
            "slot": rebooked_slot,
            "log": generate_log(user, rebooked_station, rebooked_slot),
        }

    return {
        "debug": "slot_unavailable",
        "status": "ESCALATED",
        "requested_slot": slot,
        "suggestions": suggestions,
        **escalate_issue(f"No alternative slots available for station '{station}'."),
    }


