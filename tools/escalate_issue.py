import uuid
from datetime import datetime

def escalate_issue(reason: str, severity: str = "HIGH") -> dict:
    """
    Purpose:
        Generate a structured escalation report for unresolved workflow exceptions.

    Input Schema:
        reason (str): Explanation of why the workflow is escalating.
        severity (str, optional): Escalation priority level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL". Default is "HIGH".

    Output Schema:
        {
            "status": "ESCALATED",
            "data": {
                "escalation_id": str,
                "timestamp": str,
                "severity": str,
                "reason": str,
                "recommended_action": str
            },
            "error": None
        }

    Failure Conditions:
        - reason is empty or not a string.

    Escalation Conditions:
        - None (this is the final fallback tool in the escalation state).
    """
    if not isinstance(reason, str) or not reason.strip():
        reason = "Unknown issue occurred during booking workflow execution."

    valid_severities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    sev = severity.strip().upper() if isinstance(severity, str) else "HIGH"
    if sev not in valid_severities:
        sev = "HIGH"

    # Define recommended action based on severity and reasons
    if "duplicate" in reason.lower():
        rec_action = "Contact customer to verify duplicate request intent."
    elif "no alternative" in reason.lower() or "slot" in reason.lower():
        rec_action = "Suggest custom off-peak hours or add user to booking waiting list."
    elif "file" in reason.lower() or "permission" in reason.lower() or "write" in reason.lower():
        rec_action = "ALERT SYSADMIN: File IO / database persistence failure."
        sev = "CRITICAL"
    else:
        rec_action = "Review agent execution logs and contact support team."

    escalation_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    return {
        "status": "ESCALATED",
        "data": {
            "escalation_id": escalation_id,
            "timestamp": timestamp,
            "severity": sev,
            "reason": reason,
            "recommended_action": rec_action
        },
        "error": None
    }
