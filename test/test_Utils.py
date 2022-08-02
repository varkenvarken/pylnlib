# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220802154228

# Based on LocoNet® Personal Use Edition 1.0 SPECIFICATION
# Which is © Digitrax Inc.
# See also: https://www.digitrax.com/static/apps/cms/media/documents/loconet/loconetpersonaledition.pdf
# See also: https://wiki.rocrail.net/doku.php?id=loconet:ln-pe-en

import pytest
from pytest import approx
from unittest.mock import patch
from pylnlib.Utils import Args, EnvArgs


class TestUtils:
    def test_Args(self):
        with patch("sys.argv", ["myprogram", "--help"]):
            with patch("sys.exit", lambda x:None):
                args = Args()
                assert type(args) is Args

    def test_EnvArgs(self):
        args = EnvArgs()
        assert type(args) is EnvArgs
