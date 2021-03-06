# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220801171020

# Based on LocoNet® Personal Use Edition 1.0 SPECIFICATION
# Which is © Digitrax Inc.
# See also: https://www.digitrax.com/static/apps/cms/media/documents/loconet/loconetpersonaledition.pdf
# See also: https://wiki.rocrail.net/doku.php?id=loconet:ln-pe-en

from threading import Timer
from time import sleep, time

import pytest
from pytest import approx

from pylnlib.Scrollkeeper import Scrollkeeper
from pylnlib.Slot import Slot
from pylnlib.Sensor import Sensor
from pylnlib.Switch import Switch
from pylnlib.Message import (
    SlotDataReturn,
    SensorState,
    SwitchState,
    FunctionGroup1,
    FunctionGroup2,
    FunctionGroup3,
    FunctionGroupSound,
    SlotSpeed,
)
from pylnlib.Throttle import Throttle


class mock_interface:
    def sendMessage(self, msg):
        pass


@pytest.fixture
def scrollkeeper():
    sc = Scrollkeeper(mock_interface())
    sc.dummy = True
    sc.slottrace = True
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


@pytest.fixture
def fie1():
    return FunctionGroup1(slot=3, dir=False, f2=True)


@pytest.fixture
def fie2():
    return FunctionGroup2(slot=3, f10=True)


@pytest.fixture
def fie3a():
    return FunctionGroup3(slot=3, f12=True)


@pytest.fixture
def fie3b():
    return FunctionGroup3(slot=3, f13=True)


@pytest.fixture
def fie3c():
    return FunctionGroup3(slot=3, f21=True)


@pytest.fixture
def fiesnd():
    return FunctionGroupSound(slot=3, f5=True)


@pytest.fixture
def fiespeed():
    return SlotSpeed(slot=3, speed=24)


SlotDataReturn_data = bytes(
    [
        0xE7,
        0x0E,
        0x03,
        0x01,
        0x10,
        0x30,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x34,
    ]
)


@pytest.fixture
def slotdatareturn():
    return SlotDataReturn(SlotDataReturn_data)


@pytest.fixture
def sensorstate():
    s = SensorState(3, True)
    return s


@pytest.fixture
def switchstate():
    s = SwitchState(3, thrown=True, engage=False)
    return s


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

    def test_getSwitchState(self, scrollkeeper: Scrollkeeper, switch5: Switch):
        scrollkeeper.updateSwitch(5, thrown="THROWN", engage=False)
        sw = scrollkeeper.getSwitchState(5)
        assert sw == "THROWN"

    def test_getSensorState(self, scrollkeeper: Scrollkeeper, sensor4: Sensor):
        scrollkeeper.updateSensor(4, level="ON")
        s = scrollkeeper.getSensorState(4)
        assert s == "ON"

    def test_getSlot(self, scrollkeeper: Scrollkeeper, slot3: Slot):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        assert scrollkeeper.getSlot(3) == slot3

    def test_getSensor(self, scrollkeeper: Scrollkeeper, sensor4: Sensor):
        scrollkeeper.updateSensor(4, level="ON")
        assert scrollkeeper.getSensor(4) == sensor4

    def test_getSwitch(self, scrollkeeper: Scrollkeeper, switch5: Switch):
        scrollkeeper.updateSwitch(5, thrown=True, engage=False)
        assert scrollkeeper.getSwitch(5) == switch5

    def test_getSlotIds(self, scrollkeeper: Scrollkeeper):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        assert scrollkeeper.getSlotIds() == [3]

    def test_getSensorIds(self, scrollkeeper: Scrollkeeper, sensor4: Sensor):
        scrollkeeper.updateSensor(4, level="ON")
        assert scrollkeeper.getSensorIds() == [4]

    def test_getSwitchIds(self, scrollkeeper: Scrollkeeper, switch5: Switch):
        scrollkeeper.updateSwitch(5, thrown=True, engage=False)
        assert scrollkeeper.getSwitchIds() == [5]

    def test_messageListener_slot(
        self, scrollkeeper: Scrollkeeper, slotdatareturn: SlotDataReturn
    ):
        scrollkeeper.messageListener(slotdatareturn)
        slot = scrollkeeper.getSlot(3)
        assert slot.address == 16

    def test_messageListener_sensor(
        self, scrollkeeper: Scrollkeeper, sensorstate: SensorState
    ):
        scrollkeeper.messageListener(sensorstate)
        s = scrollkeeper.getSensorState(3)
        assert s == True

    def test_messageListener_switch(
        self, scrollkeeper: Scrollkeeper, switchstate: SwitchState
    ):
        scrollkeeper.messageListener(switchstate)
        s = scrollkeeper.getSwitchState(3)
        assert s == True

    def test_messageListener_fg1(
        self, scrollkeeper: Scrollkeeper, fie1: FunctionGroup1
    ):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        scrollkeeper.messageListener(fie1)
        s = scrollkeeper.getSlot(3)
        assert s.dir == False
        assert s.f2 == True

    def test_messageListener_fg2(
        self, scrollkeeper: Scrollkeeper, fie2: FunctionGroup2
    ):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        scrollkeeper.messageListener(fie2)
        s = scrollkeeper.getSlot(3)
        assert s.f10 == True

    def test_messageListener_fg3a(
        self, scrollkeeper: Scrollkeeper, fie3a: FunctionGroup3
    ):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        scrollkeeper.messageListener(fie3a)
        s = scrollkeeper.getSlot(3)
        assert s.f12 == True

    def test_messageListener_fg3b(
        self, scrollkeeper: Scrollkeeper, fie3b: FunctionGroup3
    ):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        scrollkeeper.messageListener(fie3b)
        s = scrollkeeper.getSlot(3)
        assert s.f13 == True

    def test_messageListener_fg3c(
        self, scrollkeeper: Scrollkeeper, fie3c: FunctionGroup3
    ):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        scrollkeeper.messageListener(fie3c)
        s = scrollkeeper.getSlot(3)
        assert s.f21 == True

    def test_messageListener_fgsnd(
        self, scrollkeeper: Scrollkeeper, fiesnd: FunctionGroupSound
    ):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        scrollkeeper.messageListener(fiesnd)
        s = scrollkeeper.getSlot(3)
        assert s.f5 == True

    def test_messageListener_fgspeed(
        self, scrollkeeper: Scrollkeeper, fiespeed: SlotSpeed
    ):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        scrollkeeper.messageListener(fiespeed)
        s = scrollkeeper.getSlot(3)
        assert s.speed == 24

    def test_waitUntilLocAddressKnown(self, scrollkeeper: Scrollkeeper, slotdatareturn):
        waittime = 3.0
        Timer(waittime, lambda: scrollkeeper.messageListener(slotdatareturn)).start()
        start = time()
        result = scrollkeeper.waitUntilLocAddressKnown(16)
        end = time()
        delta = end - start
        assert result == True
        #assert delta == approx(waittime, abs=0.5)

    def test_waitUntilLocAddressKnown2(self, scrollkeeper: Scrollkeeper):
        assert not scrollkeeper.waitUntilLocAddressKnown(16, timeout=1.0)

    def test_waitUntilSensorAddressKnown(self, scrollkeeper: Scrollkeeper, sensorstate):
        waittime = 3.0
        Timer(waittime, lambda: scrollkeeper.messageListener(sensorstate)).start()
        start = time()
        result = scrollkeeper.waitUntilSensorKnown(3)
        end = time()
        delta = end - start
        assert result == True
        #assert delta == approx(waittime, abs=0.5)

    def test_waitUntilSensorAddressKnown2(self, scrollkeeper: Scrollkeeper):
        assert not scrollkeeper.waitUntilSensorKnown(3, timeout=1.0)

    def test_waitUntilSwitchAddressKnown(self, scrollkeeper: Scrollkeeper, switchstate):
        waittime = 3.0
        Timer(waittime, lambda: scrollkeeper.messageListener(switchstate)).start()
        start = time()
        result = scrollkeeper.waitUntilSwitchKnown(3)
        end = time()
        delta = end - start
        assert result == True
        #assert delta == approx(waittime, abs=0.5)

    def test_waitUntilSwitchAddressKnown2(self, scrollkeeper: Scrollkeeper):
        assert not scrollkeeper.waitUntilSwitchKnown(3, timeout=1.0)

    def test_getThrottle(self, scrollkeeper: Scrollkeeper):
        scrollkeeper.updateSlot(3, f0=True, address=12)
        t = scrollkeeper.getThrottle(12)
        assert isinstance(t, Throttle)
