# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220622154153

import argparse
import sys
import time
from threading import Thread
from time import sleep

from .Interface import Interface
from .Scrollkeeper import Scrollkeeper

CAPTUREFILE = "pylnlib.capture"


def logger(msg):
    print(time.strftime("%H:%M:%S"), msg, file=sys.stderr, flush=True)


def dumper(handle):
    """
    return a function that writes raw message data to a file.
    """

    def dumpmsg(msg):
        handle.write(msg.data)

    return dumpmsg


def reporter(scrollkeeper, interval=30):
    def dump():
        while True:
            print(scrollkeeper)
            sleep(interval)

    return dump


if __name__ == "__main__":
    cmdline = argparse.ArgumentParser()
    cmdline.add_argument(
        "-p", "--port", help="path to serial port", default="/dev/ttyACM0"
    )
    cmdline.add_argument(
        "-b", "--baud", help="baudrate of serial port", default=57600, type=int
    )
    cmdline.add_argument(
        "-i",
        "--reportinterval",
        help="interval between scrollkeeper reports",
        default=30,
        type=float,
    )
    cmdline.add_argument(
        "-c",
        "--capture",
        help=f"capture all traffic to {CAPTUREFILE}",
        action="store_true",
    )
    cmdline.add_argument(
        "-r",
        "--replay",
        help=f"replay all captured traffic from {CAPTUREFILE}",
        action="store_true",
    )
    cmdline.add_argument(
        "-f",
        "--capturefile",
        help="name of capture file",
        default=CAPTUREFILE,
        type=str,
    )

    args = cmdline.parse_args()

    # create an interface, possibly pointing to a file with previously captured input
    capturefile = None
    if args.replay:
        capturefile = open(args.capturefile, "rb")
        interface = Interface(capturefile)
    else:
        interface = Interface(args.port, args.baud)

    # always add the logger handler
    interface.receiver_handler.append(logger)

    # open a file to write raw captured bytes to
    if args.capture and not args.replay:
        capturefile = open(args.capturefile, "wb", buffering=0)
        interface.receiver_handler.append(dumper(capturefile))

    # create a Scrollkeeper instance and let it process messages
    scrollkeeper = Scrollkeeper(interface)
    interface.receiver_handler.append(scrollkeeper.messageListener)

    Thread(
        target=reporter(scrollkeeper, args.reportinterval),
        name="scrollkeeper dump",
        daemon=True,
    ).start()  # no need to join a daemon thread later

    interface.run()

    if capturefile:
        capturefile.close()

    if args.replay:
        print(
            f"waiting {args.reportinterval + 2} seconds so the final scrollkeeper report will be produced."
        )
        sleep(args.reportinterval + 2)
