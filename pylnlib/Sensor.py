# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220623123946


class Sensor:
    sensorstates = {None, "ON", "OFF"}

    def __init__(self, address, state=None):
        if state not in Sensor.sensorstates:
            raise ValueError(
                f"unknown sensor state {state}, not one of {Sensor.sensorstates}"
            )
        self.address = address
        self.level = state

    def __str__(self):
        return f"Sensor({self.address+1:2d}) = {'ON' if self.level else 'OFF'}"
