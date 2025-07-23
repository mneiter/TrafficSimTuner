import xml.etree.ElementTree as ET

class VTypesConfigUpdater:
    """
    Updates a SUMO vtypes.xml file with the specified parameters.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath

    def update(self, accel: float, tau: float, startup_delay: float) -> None:
        print(f"[INFO] Updating '{self.filepath}' with accel={accel}, tau={tau}, startupDelay={startup_delay}")
        tree = ET.parse(self.filepath)
        root = tree.getroot()

        updated = False
        for vtype in root.findall("vType"):
            vtype.set("accel", str(accel))
            vtype.set("tau", str(tau))
            vtype.set("startupDelay", str(startup_delay))
            updated = True

        if updated:
            tree.write(self.filepath)
            print(f"[INFO] Successfully wrote updated values to '{self.filepath}'")
        else:
            print(f"[WARN] No <vType> tags found in '{self.filepath}'")
