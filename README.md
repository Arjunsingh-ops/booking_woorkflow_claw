# Booking Workflow Claw ⚡

An autonomous AI-powered EV charging station booking system. OpenClaw handles natural language understanding and intent extraction, while the Python BookingAgent executes the full booking workflow through validation, tool orchestration, memory, and audit logging.

---

## Features

* Natural language booking requests via OpenClaw
* Autonomous workflow execution via BookingAgent state machine
* Separation of concerns — OpenClaw extracts intent, Python executes bookings
* Tool-based architecture (validation, slot check, booking creation)
* Workflow memory (short-term and persistent)
* Full audit trail with timestamps
* Alternative slot recommendation
* Cross-station auto-rebooking
* Duplicate booking detection
* Escalation handling
* Interactive Streamlit dashboard with reasoning visualization

---

## Architecture

```
User
  │
  ▼
Streamlit UI (app_ai.py)
  │
  ▼
OpenClaw (openclaw_client.py)
  │  ← Intent Extraction Only
  │  ← Returns: {"intent", "station", "slot", "user"}
  ▼
BookingAgent.run(intent_data)
  │
  ├── validate_station()
  ├── check_duplicate_booking()
  ├── check_slot()
  ├── find_alternative_slot()
  ├── create_booking()
  │
  ▼
bookings.json  ←  Booking persisted
  │
  ▼
audit_log.json  ←  Full audit trail
  │
  ▼
Return Confirmation to Streamlit UI
```

### Responsibility Split

| Component | Responsibility |
|-----------|---------------|
| **OpenClaw** | Understand natural language, extract structured intent |
| **BookingAgent** | State machine, validation, tool orchestration, memory, booking creation |
| **Tools** | Station validation, slot checking, booking persistence, duplicate detection |

---

## Supported Requests

```
Book Station A at 10:00 for Arjun
Reserve Station B tomorrow
Check availability
Cancel my booking
Move my booking to 11:00
Find another slot
Show bookings
Book same station again
```

---

## Agent Workflow (State Machine)

```
START
  ↓
UNDERSTAND_REQUEST (OpenClaw)
  ↓
EXTRACT_INTENT
  ↓
VALIDATE_STATION
  ↓
CHECK_DUPLICATE_BOOKING
  ↓
CHECK_SLOT
  ↓
BOOK_SLOT → SUCCESS ✅
  or
AUTO_BOOK_ALTERNATIVE → SUCCESS 🔄
  or
ESCALATE → 🚨
  ↓
END
```

---

## Project Structure

```
booking-workflow-claw/
├── app_ai.py                  # Streamlit UI (port 8501)
├── openclaw_client.py         # OpenClaw intent extraction client
├── agents/
│   └── booking_agent.py       # Autonomous booking state machine
├── tools/
│   ├── check_station.py       # Validate station exists
│   ├── check_slot.py          # Check slot availability
│   ├── create_booking.py      # Create and persist booking
│   ├── check_duplicate_booking.py  # Detect duplicate bookings
│   ├── find_alternative_slot.py    # Find nearest available slot
│   ├── escalate_issue.py      # Escalation handling
│   ├── get_booking_history.py # Retrieve booking history
│   └── log_decision.py        # Audit decision logging
├── memory/
│   └── state_manager.py       # Workflow state and memory management
├── data/
│   ├── bookings.json          # Persisted bookings
│   ├── stations.json          # Station definitions
│   └── audit_log.json         # Full audit trail
├── .env                       # API keys (GROQ_API_KEY)
├── AGENTS.md
├── TOOLS.md
├── SOUL.md
└── USER.md
```

---

## Memory

### Short-Term
* Current workflow state
* Extracted entities
* Tool outputs
* Intermediate decisions

### Persistent
* Booking history (bookings.json)
* Audit logs (audit_log.json)
* Station metadata (stations.json)

---

## Error Handling

The agent handles:

* Invalid or missing stations → asks "Which station?"
* Missing slot time → asks "What time?"
* Duplicate bookings → returns existing booking
* Slot conflicts → suggests alternatives
* Tool failures → escalation
* Missing information → targeted follow-up prompts

---

## Audit Trail

Each workflow execution records:

* User request
* Extracted intent
* Workflow state transitions
* Tool invocations (inputs/outputs)
* Agent decisions with context
* Final outcome
* Timestamps

---

## Technology Stack

* **Python 3.14**
* **Streamlit** — Interactive dashboard
* **OpenClaw CLI** — Natural language intent extraction
* **Ollama (qwen3:8b)** — Local LLM model via OpenClaw
* **JSON** — Persistent memory store

---

## Running the Project

### Prerequisites

* Python 3.10+
* Node.js (for OpenClaw CLI)
* Ollama with `qwen3:8b` model pulled

### Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate

# Install dependencies
pip install streamlit python-dotenv

# Ensure OpenClaw is installed
npm i -g openclaw

# Ensure Ollama model is available
ollama pull qwen3:8b
```

### Run

```bash
streamlit run app_ai.py
```

Open `http://localhost:8501` in your browser.

---

## Example Execution

**Input:** `Book Station A at 10:00 for Arjun`

**Flow:**
1. Streamlit → OpenClaw extracts `{"intent":"BOOK","station":"Station A","slot":"10:00","user":"Arjun"}`
2. BookingAgent.run() validates station
3. Checks for duplicate booking
4. Checks slot availability
5. Executes `create_booking()`
6. Writes to `bookings.json`
7. Returns confirmation with booking ID

**Output:**
```json
{
  "user": "Arjun",
  "station": "Station A",
  "slot": "10:00",
  "status": "CONFIRMED",
  "booking_id": "BK-..."
}
```

---

## Future Improvements

* Multi-agent coordination
* Database persistence (PostgreSQL/MongoDB)
* User authentication
* Calendar integration
* Conversation memory for follow-up commands
* Full OpenClaw tool execution integration

---

## Author

Arjun Singh
