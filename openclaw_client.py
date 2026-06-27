import subprocess
import json


def run_openclaw(prompt: str):
    cmd = [
        "openclaw",
        "agent",
        "--local",
        "--agent",
        "main",
        "--json",
        "-m",
        prompt,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }