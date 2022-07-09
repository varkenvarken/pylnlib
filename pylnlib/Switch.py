# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220625152422


class Switch:
    switchstates = {None, "CLOSED", "THROWN"}

    def __init__(self, id, thrown=None):
        if thrown not in Switch.switchstates:
            raise ValueError(
                f"unknown switch state {thrown}, not one of {Switch.switchstates}"
            )
        self.address = id
        self.thrown = thrown
        self.engage = None

    def __str__(self):
        return f"Switch(address={self.address+1}, level={'THROWN' if self.thrown else 'CLOSED'})"
