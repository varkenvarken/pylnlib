# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220626133631

import pathlib
import sys
from sys import path

# add the parent directory of the current (scripts) directory to the path so we can test without installing
d = pathlib.Path(__file__).parent.parent.resolve()
path.append(str(d))

from pylnlib.Script import Script
from pylnlib.Utils import Args, createInterface, createScrollkeeper

if __name__ == "__main__":

    args = Args().args

    # create an interface, possibly pointing to a file with previously captured input
    interface = createInterface(args)

    # create a Scrollkeeper instance and let it process messages
    scrollkeeper = createScrollkeeper(interface, args)

    # create a script instance that refers to a scrollkeeper
    s = Script(scrollkeeper)

    # start the interface in the background to process serial data
    interface.run_in_background(delay=0.1)

    # the actual scripted actions
    if s.waitForSensor(10 - 1, True):
        print("sensor 10 ON", file=sys.stderr, flush=True)
    else:
        print("sensor 10 state timeout", file=sys.stderr, flush=True)
