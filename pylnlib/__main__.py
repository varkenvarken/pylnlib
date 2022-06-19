# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220619170143

import argparse
import sys
import time

from .Interface import Interface
from .Message import FunctionGroup1, RequestSlotData

CAPTUREFILE = "pylnlib.capture"


def logger(msg):
    print(time.strftime("%H:%M:%S"), msg, file=sys.stderr, flush=True)


def dumper(handle):
    def dumpmsg(msg):
        handle.write(msg.data)

    return dumpmsg


def scrollkeeper(output):
    def scrollkeeper_assistent(msg):
        if isinstance(msg, FunctionGroup1):
            slotdatareq = RequestSlotData(msg.slot)
            print(f"sent {slotdatareq}", flush=True)
            output(slotdatareq)

    return scrollkeeper_assistent


if __name__ == "__main__":
    cmdline = argparse.ArgumentParser()
    cmdline.add_argument(
        "-p", "--port", help="path to serial port", default="/dev/ttyACM0"
    )
    cmdline.add_argument(
        "-b", "--baud", help="baudrate of serial port", default=57600, type=int
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
    args = cmdline.parse_args()

    capturefile = None

    if args.replay:
        capturefile = open(CAPTUREFILE, "rb")
        ln = Interface(capturefile)
    else:
        ln = Interface(args.port, args.baud)
    ln.receiver_handler.append(logger)
    if args.capture and not args.replay:
        capturefile = open(CAPTUREFILE, "wb", buffering=0)
        ln.receiver_handler.append(dumper(capturefile))
    ln.receiver_handler.append(scrollkeeper(ln.send_message))
    ln.run()
    if capturefile:
        capturefile.close()
