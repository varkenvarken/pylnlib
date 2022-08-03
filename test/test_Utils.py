# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220803085016

# Based on LocoNet® Personal Use Edition 1.0 SPECIFICATION
# Which is © Digitrax Inc.
# See also: https://www.digitrax.com/static/apps/cms/media/documents/loconet/loconetpersonaledition.pdf
# See also: https://wiki.rocrail.net/doku.php?id=loconet:ln-pe-en

from os import path

import pytest
from pytest import approx
from unittest.mock import patch
from pylnlib.Scrollkeeper import Scrollkeeper
from pylnlib.Utils import Args, EnvArgs, createInterface, createScrollkeeper, dumper
from pylnlib.Interface import Interface
from pylnlib.Message import CaptureTimeStamp, PowerOn, Message

thisdir = path.dirname(__file__)


@pytest.fixture
def capture1():
    return path.join(thisdir, "sample.capture")


@pytest.fixture
def args(capture1):
    class A:
        def __init__(a):
            a.replay = True
            a.capturefile = capture1
            a.fast = True
            a.log = True
            a.replay = True
            a.capture = False
            a.dummy = True
            a.slottrace = False
            a.baud = 57600
            a.port = ""

    return A()


@pytest.fixture
def interface():
    class I:
        def __init__(self):
            self.receiver_handler = []

    return I()


class TestUtils:
    def test_Args(self):
        with patch("sys.argv", ["myprogram", "--help"]):
            with patch("sys.exit", lambda x: None):
                args = Args()
                assert type(args) is Args

    def test_EnvArgs(self):
        args = EnvArgs()
        assert type(args) is EnvArgs

    def test_createInterface(self, args):
        interface = createInterface(args)
        assert type(interface) is Interface

    def test_createScrollkeeper(self, interface, args):
        scrollkeeper = createScrollkeeper(interface, args)
        assert type(scrollkeeper) is Scrollkeeper

    def test_dumper(self, tmp_path):
        filename = tmp_path / "outfile"
        with open(filename, "wb") as f:
            d = dumper(f, timestamp=True)
            d(PowerOn())
        with open(filename, "rb") as f:
            b = f.read(1000)
            assert len(b) == 8
            assert type(Message.from_data(b[:6])) is CaptureTimeStamp
            assert type(Message.from_data(b[6:])) is PowerOn
