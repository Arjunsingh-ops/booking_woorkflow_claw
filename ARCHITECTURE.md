# System Architecture


```text
                      User
                        │
                        ▼
           OpenClaw / NemoClaw Agent
                        │
                        ▼
             BookingAgent (Reasoning)
                        │
      ┌─────────────────┼─────────────────┐
      ▼                 ▼                 ▼
check_station      check_slot     duplicate_check
      │                 │                 │
      └─────────────────┼─────────────────┘
                        ▼
          find_alternative_slot
                        │
                        ▼
             create_booking
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
   bookings.json              audit_log.json
```

## Components

### Agent Layer

Responsible for:

* reasoning
* workflow orchestration
* tool selection
* exception handling
* audit generation

### Tool Layer

Each tool performs one bounded responsibility.

### Memory Layer

Persistent storage for:

* bookings

* audit trail
* station metadata


