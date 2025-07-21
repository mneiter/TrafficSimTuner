import os
import xml.etree.ElementTree as ET

VTYPES_PATH = os.path.join(os.path.dirname(__file__), "shared", "hw_model.vtypes.xml")

# Read driving behavior parameters from environment variables
ACCEL = os.environ.get("ACCEL")
TAU = os.environ.get("TAU")
STARTUP_DELAY = os.environ.get("STARTUP_DELAY")

def update_vtypes():
    tree = ET.parse(VTYPES_PATH)
    root = tree.getroot()

    for vtype in root.findall("vType"):
        if vtype.get("vClass") == "passenger":
            if ACCEL: vtype.set("accel", ACCEL)
            if TAU: vtype.set("tau", TAU)
            if STARTUP_DELAY: vtype.set("startupDelay", STARTUP_DELAY)

    tree.write(VTYPES_PATH)
    print(f"vtypes.xml updated with accel={ACCEL}, tau={TAU}, startupDelay={STARTUP_DELAY}")

if __name__ == "__main__":
    update_vtypes()
