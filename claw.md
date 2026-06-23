# Booking Workflow Claw ⚡

An intelligent EV charging station booking system with two interfaces — a standard form-based workflow and a Groq-powered AI agent that parses natural-language requests.

---

## Goal

Automatically manage EV charging bookings with smart fallback logic:
1. Book the requested slot if available.
2. Find an alternative slot at the same station if the requested one is taken.
3. **Auto-rebook** at another station if the entire station is full (toggleable).
4. Escalate with cross-station suggestions if auto-rebooking is disabled or nothing is available.

---

## Inputs

### Standard App (`app.py` — port 8501)
| Field | Type | Description |
|-------|------|-------------|
| User Name | Text | Name of the person booking |
| Station | Dropdown | Station A, B, or C |
| Preferred Slot | Dropdown | Time slot (08:00–17:00) |
| Auto-Rebook | Checkbox | Auto-book at another station if preferred is full |

### AI App (`app_ai.py` — port 8502)
| Field | Type | Description |
|-------|------|-------------|
| Booking Request | Text Area | Natural-language request (e.g. *"Book Station A at 09:00 for Arjun"*) |
| Auto-Rebook | Checkbox | Auto-book at another station if preferred is full |

---

## Tools

| # | Tool | File | Purpose |
|---|------|------|---------|
| 1 | Check Station | `tools/check_station.py` | Verify station exists in `data/stations.json` |
| 2 | Check Slot | `tools/check_slot.py` | Check if a specific slot is available at a station |
| 3 | Find Alternative Slot | `tools/find_alternative_slot.py` | Find the next available slot at the same station |
| 4 | Find Available Across Stations | `tools/find_available_across_stations.py` | List available slots at all other stations |
| 5 | Create Booking | `tools/create_booking.py` | Write a booking record to `data/bookings.json` |
| 6 | Generate Log | `tools/generate_log.py` | Create a timestamped booking log entry |
| 7 | Escalate Issue | `tools/escalate_issue.py` | Generate an escalation report when booking fails |

---

## Agents

### Standard Agent (`agents/booking_agent.py`)
Deterministic, rule-based agent. Receives structured inputs (user, station, slot, auto_rebook) and executes the workflow step by step.

### AI Agent (`agents/ai_booking_agent.py`)
Groq-powered (LLaMA 3.3 70B) agent. Parses a natural-language request via LLM to extract station, slot, and user, then follows the same booking workflow.

---

## Workflow

```
User Request
  │
  ├─ [AI Agent only] Parse natural language → extract station, slot, user
  │
  ▼
Validate Station ──── Not Found ──► FAILED
  │
  ▼
Check Slot Availability
  │
  ├─ Available ──────────────────► CONFIRMED ✅
  │
  ▼
Find Alternative Slot (same station)
  │
  ├─ Found ──────────────────────► CONFIRMED_ALTERNATIVE 🔄
  │
  ▼
Auto-Rebook Enabled?
  │
  ├─ Yes + slots at other stations ► AUTO_REBOOKED 🔄 (at another station)
  │
  ▼
Escalate ────────────────────────► ESCALATED 🚨 + cross-station suggestions
```

---

## Statuses

| Status | Meaning |
|--------|---------|
| `CONFIRMED` | Requested slot booked successfully |
| `CONFIRMED_ALTERNATIVE` | Requested slot taken; booked next available at the same station |
| `AUTO_REBOOKED` | Station fully booked; automatically booked at a different station |
| `ESCALATED` | No booking made; suggestions shown for manual selection |
| `FAILED` | Station not found or input parsing error |
| `ERROR` | Unexpected exception (AI agent only) |

---

## Data

| File | Purpose |
|------|---------|
| `data/stations.json` | Station definitions — name, location, and available time slots |
| `data/bookings.json` | All booking records — user, station, slot, and timestamp |

---

## Project Structure

```
booking-workflow-claw/
├── app.py                  # Standard booking UI (Streamlit, port 8501)
├── app_ai.py               # AI booking UI (Streamlit, port 8502)
├── agents/
│   ├── booking_agent.py    # Rule-based booking agent
│   └── ai_booking_agent.py # Groq LLM-powered booking agent
├── tools/
│   ├── check_station.py
│   ├── check_slot.py
│   ├── find_alternative_slot.py
│   ├── find_available_across_stations.py
│   ├── create_booking.py
│   ├── generate_log.py
│   └── escalate_issue.py
├── data/
│   ├── stations.json
│   └── bookings.json
├── .env                    # GROQ_API_KEY
└── claw.md                 # This file
```

---

## Running

```bash
# Standard booking app
streamlit run app.py --server.port 8501

# AI booking app (requires GROQ_API_KEY in .env)
streamlit run app_ai.py --server.port 8502
```