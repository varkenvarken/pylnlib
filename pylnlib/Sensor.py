# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220729113814

from inspect import signature

from typing import Optional, Literal, Dict, Any


class Sensor:
    """
    Represents a sensor state.

    Args:
        address: The sensor address.
        state: The sensor state.

    Raises:
        ValueError: if the state is an unknown literal and not None.

    """

    sensorstates = {None, "ON", "OFF"}

    def __init__(self, address: int, state: Optional[Literal["ON", "OFF"]] = None):
        if state not in Sensor.sensorstates:
            raise ValueError(
                f"unknown sensor state {state}, not one of {Sensor.sensorstates}"
            )
        self.address = address
        self.state = state

    def toJSON(self) -> Dict[str, Any]:
        """
        Returns an object suitable for serialiazing as JSON.

        Returns:
            Dict[str, Any]: a dictionary with the object attributes.
        """
        return {
            p: getattr(self, p)
            for p in signature(self.__init__).parameters  # type: ignore
            if p != "self"
        }

    def __str__(self) -> str:
        return f"Sensor({self.address+1:2d}) = {'ON' if self.state else 'OFF'}"

    def __eq__(self, other: object) -> bool:
        return (
            type(other) == Sensor
            and self.address == other.address
            and self.state == other.state
        )
