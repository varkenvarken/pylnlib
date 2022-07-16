# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220716180150

from inspect import signature


class Sensor:
    sensorstates = {None, "ON", "OFF"}

    def __init__(self, address, state=None):
        if state not in Sensor.sensorstates:
            raise ValueError(
                f"unknown sensor state {state}, not one of {Sensor.sensorstates}"
            )
        self.address = address
        self.state = state

    def toJSON(self):
        return {
            p: getattr(self, p)
            for p in signature(self.__init__).parameters
            if p != "self"
        }

    def __str__(self):
        return f"Sensor({self.address+1:2d}) = {'ON' if self.state else 'OFF'}"
