# based on https://github.com/andrsd/pymrrsln2

import argparse
import time

from .LocoNet import LocoNet

def str_state(state):
    if state == LocoNet.SENSOR_HI:
        return "HI"
    elif state == LocoNet.SENSOR_LO:
        return "LO"
    else:
        return "Unknown"


def recv(msg):
    print(time.strftime("%H:%M:%S") + " : ", end="")
    if args.raw:
        print(msg["raw"])
    else:
        if msg["type"] == LocoNet.MSG_POWER_ON:
            print("Global power on")
        elif msg["type"] == LocoNet.MSG_POWER_OFF:
            print("Global power off")
        elif msg["type"] == LocoNet.MSG_SWITCH_STATE:
            print("Switch id = " + str(msg["id"]) + ", state = " + str(msg["state"]))
        elif msg["type"] == LocoNet.MSG_SENSOR_STATE:
            print(
                "Sensor id = " + str(msg["id"]) + ", state = " + str_state(msg["state"])
            )
        else:
            print("Unknown message")


if __name__ == "__main__":
    cmdline = argparse.ArgumentParser()
    cmdline.add_argument(
        "--raw",
        help="Do not decode LocoNet messages, print them in raw format",
        action="store_true",
    )
    cmdline.add_argument(
        "-p", "--port", help="path to serial port", default="/dev/ttyACM0"
    )
    cmdline.add_argument(
        "-b", "--baud", help="baudrate of serial port", default=57600, type=int
    )
    args = cmdline.parse_args()

    ln = LocoNet(args.port, args.baud)
    ln.receiver_handler = recv
    ln.run()
