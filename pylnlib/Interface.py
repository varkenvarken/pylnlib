# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220801144046

import signal
import sys
import threading
from datetime import datetime
from queue import Queue
from time import sleep

import serial

from .Message import CaptureTimeStamp, Message


class Interface:
    """
    Handles thread safe sending and receiving LocoNet messages on a serial interface.

    Args:
        port (str): serial port, on Linux typically something like `/dev/ttyACM0`
        baud (int, optional): the baudrate. Defaults to 57600.
        fast (bool, optional): if false it uses timestamp message in the input data to replay a realistic speed. Defaults to False.
        dummy (bool, optional): if true it will not write anyhting on the serial port. Defaults to False.

    See Also:
        [Capture and replay](capture_and_replay)

    Example:
        ```python
        interface = Interface()
        scrollkeeper = Scrollkeeper(interface)
        interface.receiver_handler.append(scrollkeeper.messageListener)
        Thread(target=interface.run, daemon=True).start()
        ```

    It will gracefully exit if it receives a SIGINT or SIGTERM signal,
    i.e. terminate the thread that handle the input and output queues.
    """

    def __init__(
        self, port: str, baud: int = 57600, fast: bool = False, dummy: bool = False
    ):
        self.running = False
        self.time = None
        self.fast = fast
        self.dummy = dummy

        signal.signal(signal.SIGTERM, self._on_interrupt)
        signal.signal(signal.SIGINT, self._on_interrupt)

        self.exit = False
        self.capture_finished = False

        self.inputThread = threading.Thread(
            name="receiver", target=self._receiver_thread
        )
        self.inputThread.setDaemon(True)

        self.receiver_handler = []

        self.rd_event = threading.Event()

        self.inputqueue: Queue = Queue()

        self.outputThread = threading.Thread(name="sender", target=self._sender_thread)
        self.outputThread.setDaemon(True)
        self.outputqueue: Queue = Queue()

        self.input = "com"
        if type(port) == str:
            if not dummy:
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

    def _on_interrupt(self, signum, frame):
        """
        Signal handler, sets self.exit to True.

        Args:
            signum: not used
            frame : not used
        """
        self.exit = True

    def _on_receive(self, msg):
        """
        Dispatch a message object to registered handlers.

        Args:
            msg (Message): A LocoNet [Message](pylnlib.Message.md)
        """
        if self.receiver_handler != None:
            for handler in self.receiver_handler:
                handler(msg)

    def _processTimeStamp(self, msg):
        """
        Act on a [CaptureTimeStamp](pylnlib.Message.md#pylnlibmessagecapturetimestamp) messages.

        Args:
            msg (CaptureTimeStamp): a LocoNet message representing a timestamp

        If the `fast` attribute is False, this message will sleep to synchronize the replay of messages.

        !!! note
            CaptureTimeStamp is not defined in the LocoNet specification. It is defined in the pylnlib package
            and these message are added to captured datastream to allow for realistic replay of messages.
        """
        if not self.fast and self.time is not None:
            sleep(timeDiff(self.time, msg.time))
        self.time = msg.time

    def run(self, delay=0.0):
        """
        Start processing input and output.

        This will continue until an external SIGINT or SIGKILL signal is received.

        Args:
            delay (float, optional): Time in seconds to wait between incoming messages. Defaults to 0.

        Returns:
            only returns upon receiving an external signal.
        """
        self.running = True
        self.time = None

        self.inputThread.start()
        self.outputThread.start()

        # main loop that pulls messages from msg_queue
        while not self.exit:
            if self.rd_event.wait(1):
                self.rd_event.clear()

                while not self.inputqueue.empty():
                    if delay > 0:
                        sleep(delay)
                    msg = self.inputqueue.get()
                    if isinstance(msg, CaptureTimeStamp):
                        self._processTimeStamp(msg)
                    else:
                        self._on_receive(msg)

        self.inputThread.join()
        self.outputThread.join()

        self.com.close()

        print("Done...", file=sys.stderr)
        self.running = False

    def run_in_background(self, delay=0.0):
        """
        Start processing input and output and return immediately.

        Processing will continue until an external SIGINT or SIGKILL signal is received.

        Args:
            delay (float, optional): Time in seconds to wait between incoming messages. Defaults to 0.

        Returns:
            immediately.
        """
        threading.Thread(
            name="interface", target=self.run, daemon=True, args=(delay,)
        ).start()

    def _receiver_thread(self):
        """
        Read data from the interface and fill the internal input queue with messages.
        """
        while not self.exit:
            if self.dummy:
                sleep(0.1)
            elif self.input == "com":
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
            elif not self.capture_finished:
                data = self.com.read(2)
                if len(data) == 0:
                    self.capture_finished = True
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

    def _sender_thread(self):
        """
        Retrieve messages in the internal output queue and send them to the serial interface.
        """
        while not self.exit:
            if not self.outputqueue.empty():
                msg = self.outputqueue.get()
                if self.input == "com" and not self.dummy:
                    self.com.write(msg.data)
                else:  # on replay or dummy output we simply shunt back the output message
                    self.inputqueue.put(msg)
                    self.rd_event.set()
                sleep(0.25)

    def sendMessage(self, msg):
        """
        Put a message on the internal output queue.

        Args:
            msg (Message): A LocoNet [Message](pylnlib.Message.md)
        """
        self.outputqueue.put(msg)


def timeDiff(a, b):
    """
    Return the total number of seconds between  a and b.

    b MUST be later than a, so the difference between a = 23:55:49 and b = 00:05:49 will be correctly reported as 10 minutes.

    Args:
        a (datetime) : earlier timestamp
        b (datetime) : later timestamp

    Returns:
        (float) : the total number of seconds between  a and b
    """
    T = datetime.today()
    A = datetime.combine(T, a)
    B = datetime.combine(T, b)
    s = (B - A).total_seconds()
    if s < 0:
        s = 24 * 3600 - s
    return s
