# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220626133442

import argparse
import sys
import time
from atexit import register
from datetime import datetime

from .Interface import Interface
from .Message import CaptureTimeStamp
from .Scrollkeeper import Scrollkeeper

# default name of capture file
CAPTUREFILE = "pylnlib.capture"


class Args:
    """
    Common command line argument parsing.
    """

    def __init__(self):
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
            "-t",
            "--timestamp",
            help=f"add timestamps when writing to a capture file",
            action="store_true",
        )
        cmdline.add_argument(
            "-l",
            "--log",
            help=f"log received message to stderr",
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
        cmdline.add_argument(
            "-s",
            "--slottrace",
            help=f"show scrollkeeper report after every slot update",
            action="store_true",
        )

        self.args = cmdline.parse_args()


def logger(msg):
    print(time.strftime("%H:%M:%S"), msg, file=sys.stderr, flush=True)


def dumper(handle, timestamp=False):
    """
    return a function that writes raw message data to a file.
    """

    def dumpmsg(msg):
        if timestamp:
            handle.write(CaptureTimeStamp(datetime.today().time()).data)
        handle.write(msg.data)

    return dumpmsg


def reporter(scrollkeeper, interval=30):
    """
    return a function that prints the contents of a Scrollkeeper instance at regular intervals.
    """

    def dump():
        while True:
            print(scrollkeeper)
            time.sleep(interval)

    return dump


def createInterface(args):
    """
    create an interface, possibly pointing to a file with previously captured input.
    """
    capturefile = None
    if args.replay:
        capturefile = open(args.capturefile, "rb")
        interface = Interface(capturefile)
    else:
        interface = Interface(args.port, args.baud)
    if args.log:
        interface.receiver_handler.append(logger)
    # open a file to write raw captured bytes to
    if args.capture and not args.replay:
        capturefile = open(args.capturefile, "wb", buffering=0)
        interface.receiver_handler.append(dumper(capturefile, timestamp=args.timestamp))
        register(lambda f: f.close(), capturefile)
    return interface


def createScrollkeeper(interface, args):
    scrollkeeper = Scrollkeeper(interface, slottrace=args.slottrace)
    interface.receiver_handler.append(scrollkeeper.messageListener)
    return scrollkeeper
