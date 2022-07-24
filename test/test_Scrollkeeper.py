# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220724135456

# Based on LocoNet® Personal Use Edition 1.0 SPECIFICATION
# Which is © Digitrax Inc.
# See also: https://www.digitrax.com/static/apps/cms/media/documents/loconet/loconetpersonaledition.pdf
# See also: https://wiki.rocrail.net/doku.php?id=loconet:ln-pe-en

import pytest

from pylnlib.Scrollkeeper import Scrollkeeper
from pylnlib.Slot import Slot
from pylnlib.Sensor import Sensor
from pylnlib.Switch import Switch


@pytest.fixture
def scrollkeeper():
    sc = Scrollkeeper(None)
    sc.dummy = True
    return sc


@pytest.fixture
def slot3():
    sl = Slot(3, f0=True, address=12)
    return sl


@pytest.fixture
def sensor4():
    return Sensor(4, state="ON")


@pytest.fixture
def switch5():
    return Switch(5, thrown="THROWN", engage=False)


class TestScrollkeeper:
    def test_updateSlot(self, scrollkeeper: Scrollkeeper, slot3: Slot):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        assert len(scrollkeeper.slots) == 1
        assert scrollkeeper.slots[3] == slot3
        # a second time we should get the exact same results
        scrollkeeper.updateSlot(3, f0=True, address=12)
        assert len(scrollkeeper.slots) == 1
        assert scrollkeeper.slots[3] == slot3

    def test_updateSensor(self, scrollkeeper: Scrollkeeper, sensor4: Sensor):
        scrollkeeper.updateSensor(4, level="ON")
        assert len(scrollkeeper.sensors) == 1
        assert scrollkeeper.sensors[4] == sensor4
        # a second time we should get the exact same results
        scrollkeeper.updateSensor(4, level="ON")
        assert len(scrollkeeper.sensors) == 1
        assert scrollkeeper.sensors[4] == sensor4

    def test_updateSwitch(self, scrollkeeper: Scrollkeeper, switch5: Switch):
        scrollkeeper.updateSwitch(5, thrown=True, engage=False)
        assert len(scrollkeeper.switches) == 1
        assert scrollkeeper.switches[5] == switch5
        # a second time we should get the exact same results
        scrollkeeper.updateSwitch(5, thrown=True, engage=False)
        assert len(scrollkeeper.switches) == 1
        assert scrollkeeper.switches[5] == switch5

    def test_getLocoSlot(self, scrollkeeper: Scrollkeeper, slot3: Slot):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        sl = scrollkeeper.getLocoSlot(address=12)
        assert sl == slot3
