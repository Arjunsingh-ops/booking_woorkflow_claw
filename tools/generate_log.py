from datetime import datetime

def generate_log(user, station, slot):
    """Generate a confirmation log for a successful booking."""
    return {
        "status": "Confirmed",
        "user": user,
        "station": station,
        "slot": slot,
        "timestamp": datetime.now().isoformat(),
        "message": f"Booking confirmed for {user} at {station}, slot {slot}."
    }
