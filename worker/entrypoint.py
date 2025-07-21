import os
import xml.etree.ElementTree as ET
import requests
from run_simulation import run_simulation

VTYPES_PATH = "hw_model.vtypes.xml"
MASTER_URL = os.environ.get("MASTER_URL")

def update_vtypes(accel: float, tau: float, startup_delay: float):
    print(f"[INFO] Updating vtypes.xml with accel={accel}, tau={tau}, startupDelay={startup_delay}")
    tree = ET.parse(VTYPES_PATH)
    root = tree.getroot()

    for vtype in root.findall("vType"):
        vtype.set("accel", str(accel))
        vtype.set("tau", str(tau))
        vtype.set("startupDelay", str(startup_delay))

    tree.write(VTYPES_PATH)
    print("[INFO] vtypes.xml updated successfully.")

def main():
    try:
        accel = float(os.environ.get("ACCEL", "2.0"))
        tau = float(os.environ.get("TAU", "1.2"))
        startup_delay = float(os.environ.get("STARTUP_DELAY", "0"))

        print(f"[INFO] Received parameters: ACCEL={accel}, TAU={tau}, STARTUP_DELAY={startup_delay}")
        update_vtypes(accel, tau, startup_delay)

        print("[INFO] Starting simulation...")
        avg_delays = run_simulation()
        print(f"[INFO] Simulation finished. Delays: {avg_delays}")

        result = {
            "accel": accel,
            "tau": tau,
            "startupDelay": startup_delay,
            "intersection_avg_delays": avg_delays
        }

        if MASTER_URL:
            print(f"[INFO] Posting results to Master at {MASTER_URL} ...")
            resp = requests.post(MASTER_URL, json=result)
            print(f"[INFO] Master responded with status {resp.status_code}")
        else:
            print("[WARN] MASTER_URL not set. Result not sent.")

    except Exception as e:
        print(f"[ERROR] Worker failed: {e}")

if __name__ == "__main__":
    main()
