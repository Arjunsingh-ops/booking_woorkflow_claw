import json
import os

from memory.state_manager import StateManager, WorkflowState
from tools.check_station import check_station
from tools.check_slot import check_slot
from tools.create_booking import create_booking
from tools.find_alternative_slot import find_alternative_slot
from tools.check_duplicate_booking import check_duplicate_booking
from tools.get_booking_history import get_booking_history
from tools.log_decision import log_decision
from tools.escalate_issue import escalate_issue

class BookingAgent:
    def __init__(self, audit_log_path: str = None):
        self.audit_log_path = audit_log_path

    def run(self, intent_data: dict, user_request: str = "Extracted via OpenClaw", auto_rebook: bool = True) -> dict:
        """
        Runs the autonomous booking workflow end-to-end based on structured intent.
        """
        # 1. Initialize workflow memory
        state_mgr = StateManager(user_request, audit_log_path=self.audit_log_path)
        
        try:
            # Skip LLM boundary, intent is already provided by OpenClaw
            state_mgr.log_decision("Received extracted intent directly from OpenClaw.")
            
            extracted = intent_data
            state_mgr.log_intent(extracted)
            
            action = extracted.get("action", extracted.get("intent", "book"))
            station = extracted.get("station")
            slot = extracted.get("slot")
            user = extracted.get("user")

            # Validate extraction presence
            if not user or not user.strip():
                state_mgr.log_decision("User name not detected in request.")
                state_mgr.transition(WorkflowState.ESCALATE, "Missing user identity in request.")
                
                esc_result = escalate_issue("Missing booking user identity.", severity="LOW")
                state_mgr.log_tool_invocation("escalate_issue", {"reason": "Missing user"}, esc_result, "SUCCESS")
                
                state_mgr.set_final_outcome("FAILED", {"reason": "User not detected in request."})
                state_mgr.transition(WorkflowState.COMPLETE, "Workflow stopped: missing user.")
                return state_mgr.persist()

            if not station or not station.strip():
                state_mgr.log_decision("Station name not detected in request.")
                state_mgr.transition(WorkflowState.ESCALATE, "Missing station name in request.")
                
                esc_result = escalate_issue("Missing charging station location.", severity="LOW")
                state_mgr.log_tool_invocation("escalate_issue", {"reason": "Missing station"}, esc_result, "SUCCESS")
                
                state_mgr.set_final_outcome("FAILED", {"reason": "Station not detected in request."})
                state_mgr.transition(WorkflowState.COMPLETE, "Workflow stopped: missing station.")
                return state_mgr.persist()

            if not slot or not slot.strip():
                state_mgr.log_decision("Preferred slot not detected in request.")
                state_mgr.transition(WorkflowState.ESCALATE, "Missing slot time in request.")
                
                esc_result = escalate_issue("Missing charging slot time.", severity="LOW")
                state_mgr.log_tool_invocation("escalate_issue", {"reason": "Missing slot"}, esc_result, "SUCCESS")
                
                state_mgr.set_final_outcome("FAILED", {"reason": "Slot not detected in request."})
                state_mgr.transition(WorkflowState.COMPLETE, "Workflow stopped: missing slot.")
                return state_mgr.persist()

            # 3. State: VALIDATE_STATION
            state_mgr.transition(WorkflowState.VALIDATE_STATION, f"Validating existence of station '{station}'")
            
            station_check = check_station(station)
            state_mgr.log_tool_invocation("check_station", {"station_name": station}, station_check, station_check.get("status"))

            if station_check.get("status") != "SUCCESS":
                state_mgr.log_decision(f"Station validation failed: {station_check.get('error', {}).get('message')}")
                state_mgr.transition(WorkflowState.ESCALATE, f"Invalid station requested: {station}")
                
                esc_result = escalate_issue(f"Requested station '{station}' not found.", severity="LOW")
                state_mgr.log_tool_invocation("escalate_issue", {"reason": f"Station '{station}' not found"}, esc_result, "SUCCESS")
                
                state_mgr.set_final_outcome("FAILED", {"reason": f"Station '{station}' Not Found"})
                state_mgr.transition(WorkflowState.COMPLETE, "Workflow stopped: invalid station.")
                return state_mgr.persist()
                
            # Update clean station casing if needed
            station_clean = station_check["data"]["name"]

            # 4. State: CHECK_DUPLICATE_BOOKING
            state_mgr.transition(WorkflowState.CHECK_DUPLICATE_BOOKING, f"Checking if user '{user}' already booked '{station_clean}' at '{slot}'")
            
            dup_check = check_duplicate_booking(user, station_clean, slot)
            state_mgr.log_tool_invocation("check_duplicate_booking", {"user": user, "station": station_clean, "slot": slot}, dup_check, dup_check.get("status"))

            if dup_check.get("status") == "DUPLICATE":
                state_mgr.log_decision(f"Duplicate booking detected: user '{user}' has existing booking.", dup_check.get("data"))
                state_mgr.transition(WorkflowState.ESCALATE, "Duplicate booking request flagged.")
                
                esc_result = escalate_issue(f"User '{user}' already has an active booking at '{station_clean}' for '{slot}'.", severity="MEDIUM")
                state_mgr.log_tool_invocation("escalate_issue", {"reason": "Duplicate booking"}, esc_result, "SUCCESS")
                
                state_mgr.set_final_outcome("FAILED", {
                    "reason": "Duplicate Booking Detected",
                    "existing_booking": dup_check["data"]["existing_booking"]
                })
                state_mgr.transition(WorkflowState.COMPLETE, "Workflow stopped: duplicate booking.")
                return state_mgr.persist()
            elif dup_check.get("status") == "ERROR":
                state_mgr.log_decision(f"Tool error during duplicate booking check: {dup_check.get('error', {}).get('message')}")
                state_mgr.transition(WorkflowState.ESCALATE, "Tool failure during duplicate check.")
                
                esc_result = escalate_issue(f"Database error during duplicate validation: {dup_check['error']['message']}", severity="HIGH")
                state_mgr.log_tool_invocation("escalate_issue", {"reason": "Tool failure"}, esc_result, "SUCCESS")
                
                state_mgr.set_final_outcome("ERROR", {"error": dup_check["error"]})
                state_mgr.transition(WorkflowState.COMPLETE, "Workflow failed: duplicate validation tool error.")
                return state_mgr.persist()

            # 5. State: CHECK_SLOT
            state_mgr.transition(WorkflowState.CHECK_SLOT, f"Checking availability of slot '{slot}' at '{station_clean}'")
            
            slot_check = check_slot(station_clean, slot)
            state_mgr.log_tool_invocation("check_slot", {"station_name": station_clean, "slot": slot}, slot_check, slot_check.get("status"))

            if slot_check.get("status") == "AVAILABLE":
                # 6. State: BOOK_SLOT
                state_mgr.transition(WorkflowState.BOOK_SLOT, f"Requested slot '{slot}' is available. Initiating booking for '{user}'.")
                
                book_result = create_booking(user, station_clean, slot)
                state_mgr.log_tool_invocation("create_booking", {"user": user, "station": station_clean, "slot": slot}, book_result, book_result.get("status"))

                if book_result.get("status") == "SUCCESS":
                    state_mgr.log_decision(f"Booking successfully confirmed. ID: {book_result['data']['booking_id']}")
                    
                    # Log via log_decision tool for audit trail
                    log_decision(f"Confirmed booking {book_result['data']['booking_id']} for {user}", book_result["data"], "BOOK_SLOT")
                    
                    state_mgr.set_final_outcome("CONFIRMED", book_result["data"])
                    state_mgr.transition(WorkflowState.COMPLETE, "Booking confirmed successfully.")
                    return state_mgr.persist()
                else:
                    state_mgr.log_decision(f"Failed to create booking: {book_result.get('error', {}).get('message')}")
                    state_mgr.transition(WorkflowState.ESCALATE, "Booking creation persistence failure.")
                    
                    esc_result = escalate_issue(f"Database write failure while booking '{slot}' at '{station_clean}': {book_result.get('error', {}).get('message')}", severity="CRITICAL")
                    state_mgr.log_tool_invocation("escalate_issue", {"reason": "Booking persistence failure"}, esc_result, "SUCCESS")
                    
                    state_mgr.set_final_outcome("ERROR", {"error": book_result.get("error")})
                    state_mgr.transition(WorkflowState.COMPLETE, "Workflow failed: write error.")
                    return state_mgr.persist()

            elif slot_check.get("status") in ("UNAVAILABLE", "INVALID_SLOT"):
                # 7. State: AUTO_BOOK_ALTERNATIVE
                state_mgr.transition(WorkflowState.AUTO_BOOK_ALTERNATIVE, f"Slot '{slot}' is taken/invalid. Searching alternatives.")
                
                # Try finding alternative at SAME station
                alt_check = find_alternative_slot(station_clean, requested_slot=slot, cross_station=False)
                state_mgr.log_tool_invocation("find_alternative_slot", {"station_name": station_clean, "requested_slot": slot, "cross_station": False}, alt_check, alt_check.get("status"))

                if alt_check.get("status") == "FOUND":
                    alt_slot = alt_check["data"]["slot"]
                    state_mgr.log_decision(f"Alternative slot '{alt_slot}' found at same station '{station_clean}'. Initiating booking.")
                    
                    # State transition to BOOK_SLOT
                    state_mgr.transition(WorkflowState.BOOK_SLOT, f"Alternative slot found. Booking '{alt_slot}' at '{station_clean}'.")
                    
                    book_result = create_booking(user, station_clean, alt_slot)
                    state_mgr.log_tool_invocation("create_booking", {"user": user, "station": station_clean, "slot": alt_slot}, book_result, book_result.get("status"))

                    if book_result.get("status") == "SUCCESS":
                        state_mgr.log_decision(f"Alternative booking confirmed. ID: {book_result['data']['booking_id']}")
                        
                        log_decision(f"Confirmed alternative booking {book_result['data']['booking_id']} for {user}", book_result["data"], "BOOK_SLOT")
                        
                        state_mgr.set_final_outcome("CONFIRMED_ALTERNATIVE", {
                            "requested_slot": slot,
                            **book_result["data"]
                        })
                        state_mgr.transition(WorkflowState.COMPLETE, "Alternative booking confirmed successfully.")
                        return state_mgr.persist()
                    else:
                        state_mgr.log_decision(f"Failed to create alternative booking: {book_result.get('error', {}).get('message')}")
                        state_mgr.transition(WorkflowState.ESCALATE, "Alternative booking persistence failure.")
                        
                        esc_result = escalate_issue(f"Database write failure on alternative slot '{alt_slot}': {book_result.get('error', {}).get('message')}", severity="CRITICAL")
                        state_mgr.log_tool_invocation("escalate_issue", {"reason": "Alternative booking write failure"}, esc_result, "SUCCESS")
                        
                        state_mgr.set_final_outcome("ERROR", {"error": book_result.get("error")})
                        state_mgr.transition(WorkflowState.COMPLETE, "Workflow failed: write error on alternative.")
                        return state_mgr.persist()

                else:
                    # No slots at same station. Look cross-station
                    state_mgr.log_decision(f"No alternative slots available at '{station_clean}'.")
                    
                    cross_check = find_alternative_slot(station_clean, requested_slot=slot, cross_station=True)
                    state_mgr.log_tool_invocation("find_alternative_slot", {"station_name": station_clean, "requested_slot": slot, "cross_station": True}, cross_check, cross_check.get("status"))
                    
                    suggestions = cross_check.get("data", {}).get("suggestions", []) if cross_check.get("status") == "FOUND" else []

                    if auto_rebook and suggestions:
                        # Auto-rebook at first suggestion
                        s_station = suggestions[0]["station"]
                        s_slot = suggestions[0]["slot"]
                        
                        state_mgr.log_decision(f"Auto-rebooking enabled. Selected first suggestion: '{s_station}' at '{s_slot}'.")
                        state_mgr.transition(WorkflowState.BOOK_SLOT, f"Auto-rebooking at alternative station '{s_station}' for '{s_slot}'.")
                        
                        book_result = create_booking(user, s_station, s_slot)
                        state_mgr.log_tool_invocation("create_booking", {"user": user, "station": s_station, "slot": s_slot}, book_result, book_result.get("status"))

                        if book_result.get("status") == "SUCCESS":
                            state_mgr.log_decision(f"Auto-rebooked booking confirmed. ID: {book_result['data']['booking_id']}")
                            
                            log_decision(f"Confirmed auto-rebooked booking {book_result['data']['booking_id']} for {user}", book_result["data"], "BOOK_SLOT")
                            
                            state_mgr.set_final_outcome("AUTO_REBOOKED", {
                                "requested_station": station_clean,
                                "requested_slot": slot,
                                **book_result["data"]
                            })
                            state_mgr.transition(WorkflowState.COMPLETE, "Auto-rebooked booking confirmed successfully.")
                            return state_mgr.persist()
                        else:
                            state_mgr.log_decision(f"Failed to create auto-rebooked booking: {book_result.get('error', {}).get('message')}")
                            state_mgr.transition(WorkflowState.ESCALATE, "Auto-rebooked booking persistence failure.")
                            
                            esc_result = escalate_issue(f"Database write failure during auto-rebook on '{s_slot}' at '{s_station}': {book_result.get('error', {}).get('message')}", severity="CRITICAL")
                            state_mgr.log_tool_invocation("escalate_issue", {"reason": "Auto-rebook write failure"}, esc_result, "SUCCESS")
                            
                            state_mgr.set_final_outcome("ERROR", {"error": book_result.get("error")})
                            state_mgr.transition(WorkflowState.COMPLETE, "Workflow failed: write error on auto-rebook.")
                            return state_mgr.persist()

                    else:
                        # Auto-rebook disabled or no suggestions
                        state_mgr.log_decision("Cannot rebook (auto_rebook disabled or no alternative slots available cross-station). Initiating escalation.")
                        state_mgr.transition(WorkflowState.ESCALATE, "No slots available. Escalating to support.")
                        
                        esc_result = escalate_issue(f"No alternative slots available for station '{station_clean}'.", severity="HIGH")
                        state_mgr.log_tool_invocation("escalate_issue", {"reason": "No slots available"}, esc_result, "SUCCESS")
                        
                        state_mgr.set_final_outcome("ESCALATED", {
                            "station": station_clean,
                            "requested_slot": slot,
                            "suggestions": suggestions,
                            "escalation": esc_result["data"]
                        })
                        state_mgr.transition(WorkflowState.COMPLETE, "Workflow completed with escalation.")
                        return state_mgr.persist()
            else:
                # Handle error status from check_slot
                state_mgr.log_decision(f"Error checking slot availability: {slot_check.get('error', {}).get('message')}")
                state_mgr.transition(WorkflowState.ESCALATE, "Slot verification tool failure.")
                
                esc_result = escalate_issue(f"Error checking slot availability: {slot_check['error']['message']}", severity="HIGH")
                state_mgr.log_tool_invocation("escalate_issue", {"reason": "Slot check tool failure"}, esc_result, "SUCCESS")
                
                state_mgr.set_final_outcome("ERROR", {"error": slot_check["error"]})
                state_mgr.transition(WorkflowState.COMPLETE, "Workflow failed: slot check tool error.")
                return state_mgr.persist()

        except Exception as e:
            # Catch-all exception handling for auditability
            state_mgr.log_decision(f"Unexpected system error: {str(e)}")
            state_mgr.transition(WorkflowState.ESCALATE, f"Unexpected exception: {str(e)}")
            
            esc_result = escalate_issue(f"System crash: {str(e)}", severity="CRITICAL")
            state_mgr.log_tool_invocation("escalate_issue", {"reason": "System crash exception"}, esc_result, "SUCCESS")
            
            state_mgr.set_final_outcome("ERROR", {
                "error": {
                    "code": "SYSTEM_CRASH",
                    "message": str(e)
                }
            })
            state_mgr.transition(WorkflowState.COMPLETE, "Workflow failed: system exception.")
            return state_mgr.persist()
