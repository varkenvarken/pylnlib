# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220705172051

from threading import Timer


class Throttle:
    """
    A class to control a single locomotive.
    """

    def __init__(self, scrollkeeper, locaddress):
        self.scrollkeeper = scrollkeeper
        self.locaddress = locaddress

    def forward(self, speed=0.0):
        slot = self.scrollkeeper.getSlot(self.locaddress)
        dirchanged = slot.dir != False
        slot.dir = False
        speedchanged = slot.speed
        slot.setSpeed(speed)
        speedchanged = (
            speedchanged != slot.speed
        )  # compare integers; safer than double conversion to/from float
        if dirchanged:
            self.scrollkeeper.sendMessage(slot.dirMessage())
        if speedchanged:
            self.scrollkeeper.sendMessage(slot.speedMessage())

    def reverse(self, speed=0.0):
        slot = self.scrollkeeper.getSlot(self.locaddress)
        dirchanged = slot.dir != True
        slot.dir = True
        slot.setSpeed(speed)
        self.scrollkeeper.sendMessage(slot.slotWriteMessage())
        speedchanged = slot.speed
        slot.setSpeed(speed)
        speedchanged = (
            speedchanged != slot.speed
        )  # compare integers; safer than double conversion to/from float
        if dirchanged:
            self.scrollkeeper.sendMessage(slot.dirMessage())
        if speedchanged:
            self.scrollkeeper.sendMessage(slot.speedMessage())

    def lights(self, on=True, duration=0):
        slot = self.scrollkeeper.getSlot(self.locaddress)
        msg, imsg = slot.function(0, on, duration)
        self.scrollkeeper.sendMessage(msg)
        if duration > 0:
            Timer(duration, self.scrollkeeper.sendMessage, args=[imsg]).start()

    def sound(self, on=True, duration=0):
        slot = self.scrollkeeper.getSlot(self.locaddress)
        msg, imsg = slot.function(1, on, duration)
        self.scrollkeeper.sendMessage(msg)
        if duration > 0:
            Timer(duration, self.scrollkeeper.sendMessage, args=[imsg]).start()

    def whistle(self, on=True, duration=0.5):
        slot = self.scrollkeeper.getSlot(self.locaddress)
        msg, imsg = slot.function(2, on, duration)
        self.scrollkeeper.sendMessage(msg)
        if duration > 0:
            Timer(duration, self.scrollkeeper.sendMessage, args=[imsg]).start()
