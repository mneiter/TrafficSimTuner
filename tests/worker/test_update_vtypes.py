import tempfile
import xml.etree.ElementTree as ET
import pytest

from worker.update_vtypes import VTypesConfigUpdater

@pytest.fixture
def sample_vtypes_xml():
    """Fixture that returns path to a temp XML file with two <vType> entries."""
    content = """<?xml version="1.0"?>
<root>
    <vType id="car" accel="1.0" tau="1.0" startupDelay="0.0"/>
    <vType id="bus" accel="1.0" tau="1.0" startupDelay="0.0"/>
</root>
"""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".xml", delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_file.flush()
        return tmp_file.name


def test_update_vtypes_xml_correctly(sample_vtypes_xml):
    """Test that VTypesConfigUpdater updates accel, tau, and startupDelay correctly."""
    updater = VTypesConfigUpdater(sample_vtypes_xml)
    accel, tau, startup_delay = 2.5, 1.8, 0.4

    updater.update(accel, tau, startup_delay)

    tree = ET.parse(sample_vtypes_xml)
    root = tree.getroot()
    vtypes = root.findall("vType")

    assert len(vtypes) == 2
    for vtype in vtypes:
        assert vtype.attrib["accel"] == str(accel)
        assert vtype.attrib["tau"] == str(tau)
        assert vtype.attrib["startupDelay"] == str(startup_delay)


def test_update_vtypes_warns_if_no_vtype():
    """Test updater doesn't crash when <vType> elements are missing."""
    content = """<?xml version="1.0"?>
<root>
    <vehicle id="not-vtype" />
</root>
"""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".xml", delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_file.flush()

        updater = VTypesConfigUpdater(tmp_file.name)
        updater.update(1.0, 1.0, 1.0)

        tree = ET.parse(tmp_file.name)
        root = tree.getroot()
        assert len(root.findall("vType")) == 0
