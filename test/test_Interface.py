# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220801175214

# Based on LocoNet® Personal Use Edition 1.0 SPECIFICATION
# Which is © Digitrax Inc.
# See also: https://www.digitrax.com/static/apps/cms/media/documents/loconet/loconetpersonaledition.pdf
# See also: https://wiki.rocrail.net/doku.php?id=loconet:ln-pe-en

from threading import Timer
from time import sleep, time
from os import path
import pytest
from pytest import approx

from pylnlib.Interface import Interface, timeDiff
from pylnlib.Slot import Slot
from pylnlib.Sensor import Sensor
from pylnlib.Switch import Switch
from pylnlib.Message import (
    PowerOff,
    SlotDataReturn,
    SensorState,
    SwitchState,
    FunctionGroup1,
    FunctionGroup2,
    FunctionGroup3,
    FunctionGroupSound,
    SlotSpeed,
)


thisdir = path.dirname(__file__)


@pytest.fixture
def capture1():
    return path.join(thisdir, "sample.capture")


@pytest.fixture
def interface(capture1):
    return Interface(port=open(capture1, "rb"))


class TestInterface:
    def test_Init(self, interface: Interface, capsys):
        interface.run_in_background()
        sleep(1)
        interface.exit = True
        while interface.running:
            sleep(0.1)
        captured = capsys.readouterr()
        assert captured.err == "Done...\n"

    def test_receive(self, interface: Interface):
        msg = None

        def handler(m):
            nonlocal msg
            msg = m

        interface.receiver_handler.append(handler)
        interface.run_in_background()
        sleep(1)
        interface.exit = True
        while interface.running:
            sleep(0.1)
        assert msg is not None

    def test_sendMessage(self, interface: Interface):
        msg = None
        count = 0

        def handler(m):
            nonlocal msg, count
            msg = m
            count += 1

        interface.receiver_handler.append(handler)
        interface.run_in_background()
        interface.sendMessage(PowerOff())
        sleep(1)
        assert count == 2
        assert type(msg) is PowerOff

    def test_timeDiff(self):
        from datetime import time

        a = time(minute=3)
        b = time(minute=10)
        assert timeDiff(a, b) == approx(7 * 60.0)
        assert timeDiff(b, a) == approx((24 * 60 - 7) * 60.0)
