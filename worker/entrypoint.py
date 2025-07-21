import os
import subprocess
import xml.etree.ElementTree as ET
import requests
import json
import re

# Paths
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
VTYPES_PATH = os.path.join(DIR_PATH, "hw_model.vtypes.xml")
RUN_SCRIPT = os.path.join(DIR_PATH, "run_simulation.py")

# Get parameters from env
ACCEL = os.getenv("ACCEL")
TAU = os.getenv("TAU")
STARTUP_DELAY = os.getenv("STARTUP_DELAY")
MASTER_URL = os.getenv("MASTER_URL")

def update_vtypes():
    """
    Update the hw_model.vtypes.xml file with new vType parameters.
    """
    tree = ET.parse(VTYPES_PATH)
    root = tree.getroot()

    for vtype in root.findall("vType"):
        if vtype.get("vClass") == "passenger":
            if ACCEL: vtype.set("accel", ACCEL)
            if TAU: vtype.set("tau", TAU)
            if STARTUP_DELAY: vtype.set("startupDelay", STARTUP_DELAY)

    tree.write(VTYPES_PATH)
    print(f"✔ vtypes.xml updated: accel={ACCEL}, tau={TAU}, startupDelay={STARTUP_DELAY}")


def parse_output(output: str) -> dict:
    """
    Parse the printed delays from run_simulation.py
    Expected line: I2: 24.50 seconds
    """
    delays = {}
    for line in output.splitlines():
        match = re.match(r"(I\d):\s+([\d.]+)\s+seconds", line)
        if match:
            delays[match.group(1)] = float(match.group(2))
    return delays


def report_to_master(result: dict):
    """
    Send results back to the master FastAPI server.
    """
    if not MASTER_URL:
        print("⚠ MASTER_URL is not defined. Skipping report.")
        return

    payload = {
        "accel": float(ACCEL),
        "tau": float(TAU),
        "startup_delay": float(STARTUP_DELAY),
        "intersection_avg_delays": result,
        "total_error": sum((result.get(k, 0.0) - v) ** 2 for k, v in [("I2", 50.0), ("I3", 20.0)])  # <- тестовые значения
    }

    try:
        response = requests.post(MASTER_URL, json=payload)
        print(f"📡 Report sent to master: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to send report: {e}")


def main():
    update_vtypes()

    print("▶ Running SUMO simulation...")
    result = subprocess.run(
        ["python3", RUN_SCRIPT],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    delays = parse_output(result.stdout)

    if delays:
        report_to_master(delays)
    else:
        print("⚠ No delays found in output. Skipping report.")


if __name__ == "__main__":
    main()
