# Booking Workflow State Machine

```text
START
   │
   ▼
Intent Extraction
   │
   ▼
Station Validation
   │
   ├────────────── Invalid
   │                  │
   │                  ▼
   │             Escalation
   │
   ▼
Duplicate Check
   │
   ├────────────── Duplicate
   │                  │
   │                  ▼
   │             Reject Booking
   │
   ▼
Slot Availability
   │
   ├────────────── Available
   │                  │
   │                  ▼
   │            Create Booking
   │                  │
   │                  ▼
   │              SUCCESS
   │
   ▼
Alternative Search
   │
   ├────────────── Found
   │                  │
   │                  ▼
   │          Alternative Booking
   │                  │
   │                  ▼
   │              SUCCESS
   │
   ▼
Escalation
   │
   ▼
END
```
