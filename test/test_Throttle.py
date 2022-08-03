# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220803170516

# Based on LocoNet® Personal Use Edition 1.0 SPECIFICATION
# Which is © Digitrax Inc.
# See also: https://www.digitrax.com/static/apps/cms/media/documents/loconet/loconetpersonaledition.pdf
# See also: https://wiki.rocrail.net/doku.php?id=loconet:ln-pe-en

from unittest.mock import patch
import pytest

from pylnlib.Throttle import Throttle
from pylnlib.Scrollkeeper import Scrollkeeper


class mock_interface:
    def sendMessage(self, msg):
        print(msg)


@pytest.fixture(scope="class")
def scrollkeeper():
    sc = Scrollkeeper(mock_interface())
    sc.dummy = True
    sc.updateSlot(3, dir=False, speed=0, address=16)
    return sc


@pytest.fixture(scope="class")
def throttle(scrollkeeper):
    return Throttle(scrollkeeper, 16)


class TestThrottle:
    def test_forward(self, throttle, capsys):
        throttle.forward(0.5)
        captured = capsys.readouterr()
        assert (
            captured.out
            == "SlotSpeed(slot=3 speed: 15 | op = 0xa0, self.length=4, data=['a0', '03', '0f', '53'])\n"
        )

    def test_reverse(self, throttle, capsys):
        throttle.reverse(0.25)
        captured = capsys.readouterr()
        assert (
            captured.out
            == """FunctionGroup1(slot = 3 dir: True f0: None  f1: None f2: None f3: None f4: None | op = 0xa1, self.length=4, data=['0xa1', '0x3', '0x20', '0x7d'])
SlotSpeed(slot=3 speed: 8 | op = 0xa0, self.length=4, data=['a0', '03', '08', '54'])
"""
        )
