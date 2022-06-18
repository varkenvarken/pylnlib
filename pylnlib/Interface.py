# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220618154204

import signal
import sys
import threading
import time
from queue import Queue

import serial

from .Message import Message

class Interface:

    def __init__(self, port, baud):
        signal.signal(signal.SIGTERM, self.on_interrupt)
        signal.signal(signal.SIGINT, self.on_interrupt)

        self.exit = False

        self.recv = threading.Thread(name="recv", target=self.receiver_thread)
        self.recv.setDaemon(True)

        # TODO make this a subscriber list
        self.receiver_handler = None

        self.rd_event = threading.Event()

        self.msg_queue = Queue()

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

    def on_interrupt(self, signum, frame):
        self.exit = True

    def on_receive(self, msg):
        if self.receiver_handler != None:
            self.receiver_handler(msg)

    def run(self):
        self.recv.start()
        # main loop that pulls messages from msg_queue
        while not self.exit:
            n = self.rd_event.wait(1)
            if n:
                self.rd_event.clear()

                if not self.msg_queue.empty():
                    msg = self.msg_queue.get()
                    self.on_receive(msg)

        self.recv.join()
        self.com.close()

        print("Done...", file=sys.stderr)

    def receiver_thread(self):
        while not self.exit:
            if self.com != None:
                n = self.com.inWaiting()
                if n > 1:  # all messages are at least 2 bytes
                    data = self.com.read(2)
                    length = Message.length(data[0], data[1])
                    if length == 2:
                        msg = Message.from_data(data)
                    else:
                        data2 = self.com.read(length - 2)  # this is blocking, might want to change that
                        msg = Message.from_data(data+data2)
                    self.msg_queue.put(msg)
                    self.rd_event.set()
                else:
                    time.sleep(0.1)


    def send_message(self, msg):
        self.com.write(msg.data)
