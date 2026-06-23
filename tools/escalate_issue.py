from datetime import datetime

def escalate_issue(reason):
    """Return an escalation report when a booking cannot be completed."""
    return {
        "status": "Escalated",
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
        "message": f"Booking could not be completed: {reason}. Please contact support."
    }
