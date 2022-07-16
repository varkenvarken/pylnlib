# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220716125138

from inspect import signature

from .Message import (
    FunctionGroup1,
    FunctionGroup2,
    FunctionGroup3,
    FunctionGroupSound,
    SlotSpeed,
    WriteSlotData,
)


class Slot:
    speedsteps = {0: 28, 1: 28, 2: 14, 3: 128, 4: 28, 7: 128}

    def __init__(
        self,
        id,
        dir=None,
        speed=None,
        status=None,
        address=None,
        f0=None,
        f1=None,
        f2=None,
        f3=None,
        f4=None,
        f5=None,
        f6=None,
        f7=None,
        f8=None,
        f9=None,
        f10=None,
        f11=None,
        f12=None,
        trk=None,
        ss2=None,
        id1=None,
        id2=None,
    ):
        self.id = id
        self.dir = dir
        self.speed = speed
        self.status = status
        self.address = address
        self.f0 = f0
        self.f1 = f1
        self.f2 = f2
        self.f3 = f3
        self.f4 = f4
        self.f5 = f5
        self.f6 = f6
        self.f7 = f7
        self.f8 = f8
        self.f9 = f9
        self.f10 = f10
        self.f11 = f11
        self.f12 = f12
        self.trk = trk
        self.ss2 = ss2
        self.id1 = id1
        self.id2 = id2

    def __str__(self):
        ff = " ".join(
            f"f{f}:" + ("ON" if getattr(self, f"f{f}") else "OFF") for f in range(13)
        )
        return f"Slot({self.id:2d}): loc={self.address}, dir={'REVERSE' if self.dir else 'FORWARD'}, speed={self.speed}/{Slot.speedsteps[self.status&0x7]}, [{ff}]"

    def toJSON(self):
        return {
            p: getattr(self, p)
            for p in signature(self.__init__).parameters
            if p != "self"
        }

    def getSpeed(self):
        if self.speed < 2:
            return (
                self.speed
            )  # either 0 or 1 for inertial stop and emergency stop respectively
        return (self.speed - 2) / Slot.speedsteps[self.status & 0x7]

    def setSpeed(self, speed=0.0, stop=False, emergency=False):
        if stop or speed <= 0.0:
            self.speed = 0
        elif emergency:
            self.speed = 1
        else:
            self.speed = (
                2 + int(speed * Slot.speedsteps[self.status & 0x7] - 2)
                if speed > 0.0
                else 0
            )

    def slotWriteMessage(self):
        return WriteSlotData(self)

    def dirMessage(self):
        return FunctionGroup1(
            slot=self.id,
            dir=self.dir,
            f0=self.f0,
            f1=self.f1,
            f2=self.f2,
            f3=self.f3,
            f4=self.f4,
        )

    def speedMessage(self):
        return SlotSpeed(slot=self.id, speed=self.speed)

    def function(self, fie, state, duration):
        # functions are communicated as function messages,
        # but locally we keep all function info in the slot
        setattr(self, f"f{fie}", state)
        if fie <= 4:
            msg = FunctionGroup1(
                slot=self.id,
                dir=self.dir,
                f0=self.f0,
                f1=self.f1,
                f2=self.f2,
                f3=self.f3,
                f4=self.f4,
            )
        elif fie <= 8:
            msg = FunctionGroupSound(
                slot=self.id, f5=self.f5, f6=self.f6, f7=self.f7, f8=self.f8
            )
        else:
            raise NotImplementedError(
                f"function not implemented for f{fie}"
            )  # TODO create a suitable funtion message
        imsg = None
        if duration > 0.0:
            imsg, _ = self.function(fie, not state, 0)
        return msg, imsg
