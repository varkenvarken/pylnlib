# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220707161307

from threading import Timer


class Throttle:
    def __init__(self, scrollkeeper, locaddress):
        """
        A class to control a single locomotive.

        Args:
            scrollkeeper (Scrollkeeper): used to send messages and retrieve slot information
            locaddress (int): the address of the locomotive
        """
        self.scrollkeeper = scrollkeeper
        self.locaddress = locaddress

    def forward(self, speed=0.0) -> None:
        """
        Changes the speed of a locomotive to forward and a given value.

        Args:
            speed (float, optional): speed is a float in the range [0.0, 1.0], setting it to zero will initiate an inertial stop. Defaults to 0.0.

        Two LocoNet messages may be generated:

        - Only if the direction is changed: a LocoNet direction message is generated for the slot that controls this loco.
        - Only if the speed is changed: a LocoNet speed message is generated for the slot that controls this loco.
        """
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

    def reverse(self, speed=0.0) -> None:
        """
        Changes the speed of a locomotive to reverse and a given value.

        Args:
            speed (float, optional): speed is a float in the range [0.0, 1.0], setting it to zero will initiate an inertial stop. Defaults to 0.0.

        Two LocoNet messages may be generated:

        - Only if the direction is changed, a LocoNet direction message is generated for the slot that controls this loco.
        - Only if the speed is changed, a LocoNet speed message is generated for the slot that controls this loco.
        """
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

    def lights(self, on=True, duration=0) -> None:
        """
        Turn directional lights on or off.

        Args:
            on (bool, optional): new state of the directional lights. Defaults to True.
            duration (int, optional): if larger than zero will revert the lights to the previous state after duration seconds. Defaults to 0.
        """
        slot = self.scrollkeeper.getSlot(self.locaddress)
        msg, imsg = slot.function(0, on, duration)
        self.scrollkeeper.sendMessage(msg)
        if duration > 0:
            Timer(duration, self.scrollkeeper.sendMessage, args=[imsg]).start()

    def sound(self, on=True, duration=0) -> None:
        """
        Turn sound on or off.

        Args:
            on (bool, optional): new state of the  sound. Defaults to True.
            duration (int, optional): if larger than zero will revert the sound to the previous state after duration seconds. Defaults to 0.

        Returns:
            None
        """
        slot = self.scrollkeeper.getSlot(self.locaddress)
        msg, imsg = slot.function(1, on, duration)
        self.scrollkeeper.sendMessage(msg)
        if duration > 0:
            Timer(duration, self.scrollkeeper.sendMessage, args=[imsg]).start()

    def whistle(self, on=True, duration=0.5) -> None:
        """
        Sound the whistle.

        A loc decoder will typically use a short whistle sound that is silent after a short while,
        but it still needs to be turned off explicitely by the throttle, therefore the function defaults to 0.5 seconds.

        Args:
            on (bool, optional): new state of the whistle. Defaults to True.
            duration (float, optional): if larger than zero will revert the whistle to the previous state after duration seconds. Defaults to 0.5.

        """
        slot = self.scrollkeeper.getSlot(self.locaddress)
        msg, imsg = slot.function(2, on, duration)
        self.scrollkeeper.sendMessage(msg)
        if duration > 0:
            Timer(duration, self.scrollkeeper.sendMessage, args=[imsg]).start()
