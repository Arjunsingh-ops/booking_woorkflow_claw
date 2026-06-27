# EV Booking Agent Tool Specifications

This document defines the tools available to the EV Booking Autonomous Agent. Each tool has a well-defined responsibility, input contract, output contract, and error conditions.

---

# 1. check_station

## Purpose

Validate that a charging station exists and is operational.

### Input

```json
{
  "station": "Station A"
}
```

### Output

```json
{
  "exists": true,
  "status": "ACTIVE"
}
```

### Errors

* station_not_found
* station_inactive

---

# 2. check_slot

## Purpose

Determine whether a requested charging slot is available.

### Input

```json
{
  "station": "Station A",
  "slot": "09:00"
}
```

### Output

```json
{
  "available": true
}
```

### Errors

* slot_not_found
* station_invalid

---

# 3. check_duplicate_booking

## Purpose

Prevent duplicate bookings for the same user.

### Input

```json
{
  "user": "Arjun",
  "station": "Station A",
  "slot": "09:00"
}
```

### Output

```json
{
  "duplicate": false
}
```

### Errors

* duplicate_booking_detected

---

# 4. find_alternative_slot

## Purpose

Locate the nearest available charging slot when the requested slot is unavailable.

### Input

```json
{
  "station": "Station A",
  "requested_slot": "09:00"
}
```

### Output

```json
{
  "station": "Station A",
  "slot": "16:00"
}
```

### Errors

* no_alternative_found

---

# 5. create_booking

## Purpose

Persist a confirmed booking.

### Input

```json
{
  "user": "Arjun",
  "station": "Station A",
  "slot": "16:00"
}
```

### Output

```json
{
  "booking_id": "<uuid>",
  "status": "CONFIRMED"
}
```

### Errors

* booking_failed
* persistence_error

---

# 6. get_booking_history

## Purpose

Retrieve historical bookings for a user.

### Input

```json
{
  "user": "Arjun"
}
```

### Output

```json
{
  "bookings": []
}
```

### Errors

* user_not_found

---

# 7. log_decision

## Purpose

Record every workflow decision for auditability.

### Input

```json
{
  "state": "CHECK_SLOT",
  "decision": "Slot unavailable"
}
```

### Output

```json
{
  "logged": true
}
```

### Errors

* log_write_failed

---

# 8. escalate_issue

## Purpose

Escalate unresolved workflow failures.

### Input

```json
{
  "reason": "No slots available"
}
```

### Output

```json
{
  "status": "ESCALATED"
}
```

### Errors

* escalation_service_unavailable

---

# Tool Execution Principles

The agent must:

* Validate all inputs before invoking tools.
* Execute tools in workflow order.
* Never bypass validation.
* Record every tool invocation in the audit log.
* Escalate instead of guessing when tools fail.
