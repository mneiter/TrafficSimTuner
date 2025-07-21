import os
import subprocess
import requests
import json
import re
from update_vtypes import update_vtypes

# Paths
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
RUN_SCRIPT = os.path.join(DIR_PATH, "run_simulation.py")

# Env
ACCEL = os.getenv("ACCEL")
TAU = os.getenv("TAU")
STARTUP_DELAY = os.getenv("STARTUP_DELAY")
MASTER_URL = os.getenv("MASTER_URL")

def parse_output(output: str) -> dict:
    delays = {}
    for line in output.splitlines():
        match = re.match(r"(I\d):\s+([\d.]+)\s+seconds", line)
        if match:
            delays[match.group(1)] = float(match.group(2))
    return delays

def report_to_master(result: dict):
    if not MASTER_URL:
        print("MASTER_URL is not defined. Skipping report.")
        return

    payload = {
        "accel": float(ACCEL),
        "tau": float(TAU),
        "startup_delay": float(STARTUP_DELAY),
        "intersection_avg_delays": result,
        "total_error": sum((result.get(k, 0.0) - v) ** 2 for k, v in [("I2", 50.0), ("I3", 20.0)])
    }

    try:
        response = requests.post(MASTER_URL, json=payload)
        print(f"Report sent to master: {response.status_code}")
    except Exception as e:
        print(f"Failed to send result: {e}")

def main():
    update_vtypes()

    result = subprocess.run(
        ["python3", RUN_SCRIPT],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    parsed = parse_output(result.stdout)
    report_to_master(parsed)

if __name__ == "__main__":
    main()
