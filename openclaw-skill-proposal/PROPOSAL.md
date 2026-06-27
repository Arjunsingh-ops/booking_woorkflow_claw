
# EV Booking Skill Proposal

## Summary

Create a workspace skill named `ev-booking` that helps users manage EV charging station bookings.

## Goal

Reuse the existing Python EV booking application instead of replacing it.

The skill should guide the OpenClaw agent to:

- Check station availability
- Check slot availability
- Detect duplicate bookings
- Suggest alternative slots
- Create bookings
- Retrieve booking history
- Escalate booking issues when needed

## Existing implementation

The project already contains:

- agents/booking_agent.py
- tools/check_station.py
- tools/check_slot.py
- tools/check_duplicate_booking.py
- tools/find_alternative_slot.py
- tools/create_booking.py
- tools/get_booking_history.py
- data/bookings.json
- data/stations.json

## Desired behavior

When a user asks to book or manage an EV charging session, OpenClaw should use this skill and invoke the existing booking workflow instead of creating a new implementation.

