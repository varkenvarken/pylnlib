# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220626155843

import signal
import sys
import threading
from time import sleep
from datetime import datetime
from queue import Queue

import serial

from .Message import CaptureTimeStamp, Message


class Interface:
    def __init__(self, port, baud=57600):

        self.time = None

        signal.signal(signal.SIGTERM, self.on_interrupt)
        signal.signal(signal.SIGINT, self.on_interrupt)

        self.exit = False

        self.inputThread = threading.Thread(
            name="receiver", target=self.receiver_thread
        )
        self.inputThread.setDaemon(True)

        self.receiver_handler = []

        self.rd_event = threading.Event()

        self.inputqueue = Queue()

        self.outputThread = threading.Thread(name="sender", target=self.sender_thread)
        self.outputThread.setDaemon(True)
        self.outputqueue = Queue()

        self.input = "com"
        if type(port) == str:
            try:
                # 8 bits, 1 stop bit, 1 start bit
                self.com = serial.Serial(
                    port=port,
                    baudrate=baud,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=None,
                )
            except serial.SerialException as e:
                exit(e)
        else:
            self.input = "file"
            self.com = port

    def on_interrupt(self, signum, frame):
        self.exit = True

    def on_receive(self, msg):
        if self.receiver_handler != None:
            for handler in self.receiver_handler:
                handler(msg)

    def processTimeStamp(self, msg):
        if self.time is not None:
            sleep(timeDiff(self.time, msg.time))
        self.time = msg.time

    def run(self, delay=0):

        self.time = None

        self.inputThread.start()
        self.outputThread.start()

        # main loop that pulls messages from msg_queue
        while not self.exit:
            if self.rd_event.wait(1):
                self.rd_event.clear()

                while not self.inputqueue.empty():
                    sleep(delay)
                    msg = self.inputqueue.get()
                    if isinstance(msg, CaptureTimeStamp):
                        self.processTimeStamp(msg)
                    else:
                        self.on_receive(msg)

        while not self.inputqueue.empty():
            sleep(delay)
            msg = self.inputqueue.get()
            if isinstance(msg, CaptureTimeStamp):
                self.processTimeStamp(msg)
            else:
                self.on_receive(msg)

        self.inputThread.join()
        self.outputThread.join()

        self.com.close()

        print("Done...", file=sys.stderr)

    def run_in_background(self, delay):
        threading.Thread(
            name="interface", target=self.run, daemon=True, args=(delay,)
        ).start()

    def receiver_thread(self):
        while not self.exit:
            if self.input == "com":
                n = self.com.inWaiting()
                if n > 1:  # all messages are at least 2 bytes
                    data = self.com.read(2)
                    length = Message.length(data[0], data[1])
                    if length == 2:
                        msg = Message.from_data(data)
                    else:
                        data2 = self.com.read(
                            length - 2
                        )  # this is blocking, might want to change that
                        msg = Message.from_data(data + data2)
                    self.inputqueue.put(msg)
                    self.rd_event.set()
                else:
                    sleep(0.1)
            else:
                data = self.com.read(2)
                # print(len(data), list(map(hex, data)))

                if len(data) == 0:
                    self.exit = True
                elif len(data) < 2:
                    raise IOError("captured stream ended prematurely")
                else:
                    length = Message.length(data[0], data[1])
                    if length == 2:
                        msg = Message.from_data(data)
                    else:
                        data2 = self.com.read(length - 2)
                        if len(data2) < length - 2:
                            raise IOError("captured stream ended prematurely")
                        msg = Message.from_data(data + data2)
                    self.inputqueue.put(msg)
                self.rd_event.set()

    def sender_thread(self):
        while not self.exit:
            if not self.outputqueue.empty():
                msg = self.outputqueue.get()
                if self.input == "com":
                    self.com.write(msg.data)
                else:  # on replay we simply shunt back the output message
                    self.inputqueue.put(msg)
                    self.rd_event.set()
                sleep(0.25)

    def sendMessage(self, msg):
        self.outputqueue.put(msg)


def timeDiff(a, b):
    """
    return the total number of seconds between  a and b.

    b MUST be later than a, so the difference between a = 23:55:49 and b = 00:05:49 will be correctly reported as 10 minutes.
    """
    T = datetime.today()
    A = datetime.combine(T, a)
    B = datetime.combine(T, b)
    s = ((B - A).total_seconds())
    if s < 0:
        s = 24 * 3600 - s
    return s
