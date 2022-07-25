# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220725134115

# Based on LocoNet® Personal Use Edition 1.0 SPECIFICATION
# Which is © Digitrax Inc.
# See also: https://www.digitrax.com/static/apps/cms/media/documents/loconet/loconetpersonaledition.pdf
# See also: https://wiki.rocrail.net/doku.php?id=loconet:ln-pe-en

import pytest
from pytest import approx

from pylnlib.Slot import Slot
from pylnlib.Message import SlotDataReturn, SensorState, SwitchState


@pytest.fixture
def slot():
    return Slot(3, dir=True, speed=0.5, address=17, f0=True, f1=True)


class TestSlot:
    def test_Slot_init(self, slot: Slot):
        assert slot.dir == True
        assert slot.speed == 15
        assert slot.address == 17
        assert slot.f0 == True
        assert slot.f1 == True
        assert slot.f2 == None
        assert slot == slot

    def test_Slot_toJSON(self, slot: Slot):
        assert slot.toJSON() == {
            "id": 3,
            "speed": 0.5,
            "address": 17,
            "dir": True,
            "f0": True,
            "f1": True,
            "f2": None,
            "f3": None,
            "f4": None,
            "f5": None,
            "f6": None,
            "f7": None,
            "f8": None,
            "f9": None,
            "f10": None,
            "f11": None,
            "f12": None,
            "id1": None,
            "id2": None,
            "ss2": None,
            "status": 0,
            "trk": None,
        }

    def test_Slot_getSpeed(self, slot: Slot):
        assert 0.5 == approx(
            slot.getSpeed()
        )  # status == 0 -> effective speedsteps == 26

    def test_Slot_setSpeed(self, slot: Slot):
        slot.setSpeed(0.25)
        assert 0.25 == approx(
            slot.getSpeed(), abs=0.5 / 26
        )  # status == 0 -> effective speedsteps == 26
