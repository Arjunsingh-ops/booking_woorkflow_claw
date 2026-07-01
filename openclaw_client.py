import subprocess
import json

OPENCLAW = r"C:\Users\arjun\AppData\Roaming\npm\openclaw.cmd"


def run_openclaw(user_request: str):

    system_prompt = (
        "You are an EV Charging Booking Assistant. "
        "Extract the booking details from the user's request. "
        "Return ONLY valid JSON. "
        'Example: {"intent":"BOOK","station":"Station A","slot":"10:00","user":"Arjun"} '
        "Do not add markdown. Do not explain."
    )

    prompt = f"{system_prompt} User Request: {user_request}"

    cmd = [
        OPENCLAW,
        "infer",
        "model",
        "run",
        "--local",
        "--model",
        "ollama/qwen3:8b",
        "--prompt",
        prompt,
    ]

    print("Running:", cmd)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }