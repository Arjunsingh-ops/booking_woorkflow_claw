import json
import os
import uuid
from datetime import datetime

def log_decision(decision: str, context: dict, state: str) -> dict:
    """
    Purpose:
        Persist a specific agent decision, along with its execution context and state, to the audit log.

    Input Schema:
        decision (str): The decision description/reasoning.
        context (dict): The variables or state surrounding the decision.
        state (str): The state in which the decision was made.

    Output Schema:
        {
            "status": "SUCCESS" | "ERROR",
            "data": {
                "decision_id": str,
                "timestamp": str,
                "state": str,
                "decision": str
            } | None,
            "error": {
                "code": str,
                "message": str
            } | None
        }

    Failure Conditions:
        - decision or state is missing or not a string.
        - context is not a dictionary.
        - File write failure for audit_log.json.

    Escalation Conditions:
        - None.
    """
    # Validation
    if not isinstance(decision, str) or not decision.strip():
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "INVALID_INPUT",
                "message": "Decision must be a non-empty string."
            }
        }
    if not isinstance(state, str) or not state.strip():
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "INVALID_INPUT",
                "message": "State must be a non-empty string."
            }
        }
    if not isinstance(context, dict):
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "INVALID_INPUT",
                "message": "Context must be a dictionary."
            }
        }

    audit_path = os.path.join(os.path.dirname(__file__), "..", "data", "audit_log.json")
    decision_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    decision_record = {
        "record_type": "independent_decision",
        "decision_id": decision_id,
        "timestamp": timestamp,
        "state": state.strip(),
        "decision": decision.strip(),
        "context": context
    }

    try:
        if not os.path.exists(audit_path):
            logs = []
        else:
            with open(audit_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
            if not isinstance(logs, list):
                logs = []
    except Exception:
        logs = []

    logs.append(decision_record)

    try:
        os.makedirs(os.path.dirname(audit_path), exist_ok=True)
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except IOError as e:
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "WRITE_FAILURE",
                "message": f"Failed to write decision to audit log: {str(e)}"
            }
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "data": None,
            "error": {
                "code": "UNEXPECTED_ERROR",
                "message": str(e)
            }
        }

    return {
        "status": "SUCCESS",
        "data": {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "state": state.strip(),
            "decision": decision.strip()
        },
        "error": None
    }
