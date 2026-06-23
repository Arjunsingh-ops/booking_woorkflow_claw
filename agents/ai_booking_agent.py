from dotenv import load_dotenv
import os
import json
from groq import Groq

from tools.check_station import check_station
from tools.check_slot import check_slot
from tools.create_booking import create_booking
from tools.find_alternative_slot import find_alternative_slot
from tools.generate_log import generate_log
from tools.escalate_issue import escalate_issue
from tools.find_available_across_stations import find_available_across_stations

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=api_key)


def ai_booking_agent(user_request, auto_rebook=True):

    prompt = f"""
You are an EV Charging Booking Agent.

Extract the booking information from the user's request.

Return ONLY valid JSON.

Example:

{{
    "action": "book",
    "station": "Station A",
    "slot": "09:00",
    "user": "Arjun"
}}

User Request:
{user_request}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an EV Charging Booking Agent. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        print("RAW GROQ RESPONSE:")
        print(response.choices[0].message.content)

        cleaned = (
            response.choices[0].message.content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        decision = json.loads(cleaned)

        print("PARSED DECISION:")
        print(decision)

        station = decision.get("station")
        slot = decision.get("slot")
        user = decision.get("user", "Guest")

        if not station:
            return {
                "status": "FAILED",
                "reason": "Station not detected"
            }

        if not slot:
            return {
                "status": "FAILED",
                "reason": "Slot not detected"
            }

        # TOOL 1 — Verify station exists
        station_data = check_station(station)

        if not station_data:
            return {
                "status": "FAILED",
                "reason": "Station Not Found"
            }

        # TOOL 2 — Check if requested slot is available
        available = check_slot(station, slot)

        if available:
            # TOOL 3 — Book the requested slot
            create_booking(user, station, slot)

            return {
                "status": "BOOKED",
                "user": user,
                "station": station,
                "slot": slot,
                "log": generate_log(user, station, slot),
            }

        # TOOL 4 — Requested slot unavailable: find an alternative
        alternative = find_alternative_slot(station, slot)

        if alternative:
            # TOOL 5 — Book the alternative slot automatically
            create_booking(user, station, alternative)

            return {
                "status": "CONFIRMED_ALTERNATIVE",
                "user": user,
                "station": station,
                "requested_slot": slot,
                "booked_slot": alternative,
                "log": generate_log(user, station, alternative),
            }

        # No alternatives exist — suggest slots at other stations
        suggestions = find_available_across_stations(exclude_station=station)

        if auto_rebook and suggestions:
            rebooked_station = suggestions[0]["station"]
            rebooked_slot = suggestions[0]["slot"]
            create_booking(user, rebooked_station, rebooked_slot)

            return {
                "status": "AUTO_REBOOKED",
                "user": user,
                "requested_station": station,
                "requested_slot": slot,
                "station": rebooked_station,
                "slot": rebooked_slot,
                "log": generate_log(user, rebooked_station, rebooked_slot),
            }

        return {
            "status": "ESCALATED",
            "user": user,
            "station": station,
            "requested_slot": slot,
            "suggestions": suggestions,
            **escalate_issue(
                f"No alternative slots available at '{station}'. Original slot '{slot}' was unavailable."
            ),
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e)
        }