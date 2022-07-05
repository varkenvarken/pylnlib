# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220705170642

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
    t = s.getThrottle(4)
    s.wait(1)
    t.lights()  # directional lights on
    s.wait(1)
    t.sound()  # sound on
    s.wait(1)
    t.whistle()  # will turn of automatically
    s.wait(1)
    t.sound(False)  # sound off
    s.wait(1)
    t.lights(False)  # directional lights off
    s.wait(1)  # this just to give the receiver thread a chance to callback a logger
