import tempfile
import xml.etree.ElementTree as ET
from worker.update_vtypes import VTypesConfigUpdater


def create_sample_vtypes_xml():
    """Create a temporary vtypes XML file and return its path."""
    xml_content = """<?xml version="1.0"?>
<root>
    <vType id="car" accel="1.0" tau="1.0" startupDelay="0.0"/>
    <vType id="bus" accel="1.0" tau="1.0" startupDelay="0.0"/>
</root>
"""
    tmp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".xml", delete=False)
    tmp_file.write(xml_content)
    tmp_file.flush()
    return tmp_file.name


def test_update_vtypes_xml_correctly():
    xml_path = create_sample_vtypes_xml()
    updater = VTypesConfigUpdater(xml_path)

    # Values to update
    accel = 2.5
    tau = 1.8
    startup_delay = 0.4

    updater.update(accel, tau, startup_delay)

    tree = ET.parse(xml_path)
    root = tree.getroot()
    vtypes = root.findall("vType")

    assert len(vtypes) == 2
    for vtype in vtypes:
        assert vtype.attrib["accel"] == str(accel)
        assert vtype.attrib["tau"] == str(tau)
        assert vtype.attrib["startupDelay"] == str(startup_delay)


def test_update_vtypes_warns_if_no_vtype():
    xml_content = """<?xml version="1.0"?>
<root>
    <vehicle id="not-vtype" />
</root>
"""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".xml", delete=False) as tmp_file:
        tmp_file.write(xml_content)
        tmp_file.flush()
        updater = VTypesConfigUpdater(tmp_file.name)

        # Nothing to update but should not raise error
        updater.update(1.0, 1.0, 1.0)

        tree = ET.parse(tmp_file.name)
        root = tree.getroot()
        assert len(root.findall("vType")) == 0
