# Agent Reasoning Sequence

```text
User Request
      │
      ▼
Extract Intent
      │
      ▼
Understand Booking Goal
      │
      ▼
Choose Required Tools
      │
      ▼
Execute Tool Chain
      │
      ▼
Evaluate Outputs
      │
      ▼
Need Alternative?
      │
      ├──── Yes ──► Search Alternative
      │
      └──── No
      │
      ▼
Create Booking
      │
      ▼
Write Audit
      │
      ▼
Return Final Response
```

## Reasoning Principles

The agent must:

* Think before acting.
* Validate before booking.
* Never invent booking confirmations.
* Record every important decision.
* Escalate instead of guessing.
