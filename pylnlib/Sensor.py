# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220801132322

from inspect import signature


class Sensor:
    """
    Represents a sensor state.

    Args:
        address: int The sensor address.
        state: The sensor state, one of {None, "ON", "OFF"}

    Raises:
        ValueError: if the state is an unknown literal and not None.
    """

    sensorstates = {None, "ON", "OFF"}

    def __init__(self, address, state=None):
        if state not in Sensor.sensorstates:
            raise ValueError(
                f"unknown sensor state {state}, not one of {Sensor.sensorstates}"
            )
        self.address = address
        self.state = state

    def toJSON(self):
        """
        Returns an object suitable for serialiazing as JSON.

        Returns:
            dict: A dictionary with the object attributes.
        """
        return {
            p: getattr(self, p)
            for p in signature(self.__init__).parameters
            if p != "self"
        }

    def __str__(self):
        """
        Returns a string representation of a Sensor object.

        !!! note
            The address shown is 1 larger than the actual address as is customary. (The address is indeed offset 0, but modellers are not accustomed to that)

        Returns:
            str: the string representation of a Sensor object with its state and address.
        """
        return f"Sensor({self.address+1:2d}) = {'ON' if self.state else 'OFF'}"

    def __eq__(self, other: object):
        """
        Compares a Sensor object to another object.

        Args:
            other (object): any other object

        Returns:
            bool: True if sensor address and states are the same
        """
        return (
            type(other) == Sensor
            and self.address == other.address
            and self.state == other.state
        )
