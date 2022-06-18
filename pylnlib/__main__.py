# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220618154130

import argparse
import time

from .Interface import Interface

def recv(msg):
    print(time.strftime("%H:%M:%S"), msg)

if __name__ == "__main__":
    cmdline = argparse.ArgumentParser()
    cmdline.add_argument(
        "-p", "--port", help="path to serial port", default="/dev/ttyACM0"
    )
    cmdline.add_argument(
        "-b", "--baud", help="baudrate of serial port", default=57600, type=int
    )
    args = cmdline.parse_args()

    ln = Interface(args.port, args.baud)
    ln.receiver_handler = recv
    ln.run()
