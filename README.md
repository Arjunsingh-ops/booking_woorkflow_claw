# Booking Workflow Claw

An autonomous AI agent for EV charging station booking built using the Claw ecosystem. The agent owns the complete booking workflow through reasoning, tool orchestration, workflow memory, exception handling, and auditability.

---

# Features

* Natural language booking requests
* Autonomous workflow execution
* Tool-based architecture
* Workflow memory
* Audit trail
* Alternative slot recommendation
* Duplicate booking detection
* Escalation handling
* Interactive Streamlit dashboard
* OpenClaw-compatible skill specification

---

# Architecture

```
                  User
                    │
                    ▼
           OpenClaw / NemoClaw
                    │
                    ▼
            BookingAgent.run()
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
check_station   check_slot   duplicate_check
      │             │             │
      └─────────────┼─────────────┘
                    ▼
        find_alternative_slot
                    │
                    ▼
           create_booking
                    │
                    ▼
          bookings.json
                    │
                    ▼
            audit_log.json
```

---

# Agent Workflow

```
START

↓

Intent Extraction

↓

Station Validation

↓

Duplicate Booking Check

↓

Slot Availability Check

↓

Booking

↓

SUCCESS

OR

Alternative Search

↓

Alternative Booking

↓

SUCCESS

OR

Escalation
```

---

# Project Structure

```
booking-workflow-claw/

├── agents/
│   └── booking_agent.py
│
├── tools/
│   ├── check_station.py
│   ├── check_slot.py
│   ├── create_booking.py
│   ├── check_duplicate_booking.py
│   ├── find_alternative_slot.py
│   ├── escalate_issue.py
│   ├── get_booking_history.py
│   └── log_decision.py
│
├── data/
│   ├── bookings.json
│   ├── stations.json
│   └── audit_log.json
│
├── memory/
│
├── app_ai.py
├── app_openclaw.py
├── AGENTS.md
├── TOOLS.md
├── SOUL.md
└── USER.md
```

---

# Memory

## Short-Term

* Current workflow state
* Extracted entities
* Tool outputs
* Decisions

## Persistent

* Booking history
* Audit logs
* Station metadata

---

# Exception Handling

The agent handles:

* Invalid stations
* Duplicate bookings
* Slot conflicts
* Alternative slot allocation
* Missing information
* Tool failures
* Escalation scenarios

---

# Audit Trail

Each workflow execution records:

* User request
* Workflow state transitions
* Tool invocations
* Agent decisions
* Final outcome
* Timestamp

---

# Technology Stack

* Python
* Streamlit
* Groq LLM
* OpenClaw / NemoClaw
* JSON Memory Store

---

# Running the Project

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app_ai.py
```

Run the CLI:

```bash
python app_openclaw.py
```

---

# Future Improvements

* Multi-agent coordination
* Database persistence
* Authentication
* Calendar integration
* Additional Eko workflow templates
* Full OpenClaw tool execution integration

---

# Author

Arjun Singh
