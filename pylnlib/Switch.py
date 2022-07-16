# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220716125619

from inspect import signature


class Switch:
    switchstates = {None, "CLOSED", "THROWN"}

    def __init__(self, id, thrown=None):
        if thrown not in Switch.switchstates:
            raise ValueError(
                f"unknown switch state {thrown}, not one of {Switch.switchstates}"
            )
        self.id = id
        self.thrown = thrown
        self.engage = None

    def toJSON(self):
        return {
            p: getattr(self, p)
            for p in signature(self.__init__).parameters
            if p != "self"
        }

    def __str__(self):
        return f"Switch(address={self.id+1}, level={'THROWN' if self.thrown else 'CLOSED'})"
