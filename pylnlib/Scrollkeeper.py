# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220626134054

from datetime import datetime
from time import sleep
from threading import Lock

from .Message import (
    FunctionGroup1,
    FunctionGroup2,
    FunctionGroupSound,
    RequestLocAddress,
    RequestSlotData,
    RequestSwitchState,
    SensorState,
    SlotDataReturn,
    SlotSpeed,
    SwitchState,
)
from .Sensor import Sensor
from .Slot import Slot
from .Switch import Switch


class Scrollkeeper:
    def __init__(self, interface, slottrace=False):
        self.interface = interface
        self.slottrace = slottrace
        self.slots = {}
        self.slotlock = Lock()
        self.switches = {}
        self.switchlock = Lock()
        self.sensors = {}
        self.sensorlock = Lock()

    def messageListener(self, msg):
        """
        Handles incoming messages and updates internal state.

        If information refering an unknown slot comes in, it will issue a slot status request.
        """
        if isinstance(msg, SlotDataReturn):

            self.updateSlot(
                msg.slot,
                address=msg.address,
                dir=msg.dir,
                speed=msg.speed,
                f0=msg.f0,
                f1=msg.f1,
                f2=msg.f2,
                f3=msg.f3,
                f4=msg.f4,
                f5=msg.f5,
                f6=msg.f6,
                f7=msg.f7,
                f8=msg.f8,
                status=msg.status,
                ss2=msg.ss2,
                trk=msg.trk,
                id1=msg.id1,
                id2=msg.id2,
            )
        elif isinstance(msg, FunctionGroup1):
            if msg.slot not in self.slots:
                self.sendMessage(RequestSlotData(msg.slot))
            else:
                self.updateSlot(
                    msg.slot,
                    dir=msg.dir,
                    f0=msg.f0,
                    f1=msg.f1,
                    f2=msg.f2,
                    f3=msg.f3,
                    f4=msg.f4,
                )
        elif isinstance(msg, FunctionGroupSound):
            if msg.slot not in self.slots:
                self.sendMessage(RequestSlotData(msg.slot))
            else:
                self.updateSlot(
                    msg.slot,
                    f5=msg.f5,
                    f6=msg.f6,
                    f7=msg.f7,
                    f8=msg.f8,
                )
        elif isinstance(msg, FunctionGroup2):
            if msg.slot not in self.slots:
                self.sendMessage(RequestSlotData(msg.slot))
            else:
                self.updateSlot(
                    msg.slot,
                    f9=msg.f9,
                    f10=msg.f10,
                    f11=msg.f11,
                    f12=msg.f12,
                )
        elif isinstance(msg, SlotSpeed):
            if msg.slot not in self.slots:
                self.sendMessage(RequestSlotData(msg.slot))
            else:
                self.updateSlot(
                    msg.slot,
                    speed=msg.speed,
                )
        elif isinstance(msg, SensorState):
            self.updateSensor(msg.address, msg.level)
        elif isinstance(msg, SwitchState):
            self.updateSwitch(msg.address, msg.thrown, msg.engage)

    def updateSlot(
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
        with self.slotlock:
            if id not in self.slots:
                self.slots[id] = Slot(id)

            slot = self.slots[id]
            slot.slot = id
            if dir is not None:
                slot.dir = dir
            if speed is not None:
                slot.speed = speed
            if status is not None:
                slot.status = status
            if address is not None:
                slot.address = address
            if f0 is not None:
                slot.f0 = f0
            if f1 is not None:
                slot.f1 = f1
            if f2 is not None:
                slot.f2 = f2
            if f3 is not None:
                slot.f3 = f3
            if f4 is not None:
                slot.f4 = f4
            if f5 is not None:
                slot.f5 = f5
            if f6 is not None:
                slot.f6 = f6
            if f7 is not None:
                slot.f7 = f7
            if f8 is not None:
                slot.f8 = f8
            if f9 is not None:
                slot.f9 = f9
            if f10 is not None:
                slot.f10 = f10
            if f11 is not None:
                slot.f11 = f11
            if f8 is not None:
                slot.f12 = f12
            if trk is not None:
                slot.trk = trk
            if ss2 is not None:
                slot.ss2 = ss2
            if id1 is not None:
                slot.id1 = id1
            if id2 is not None:
                slot.id2 = id2
            if self.slottrace:
                print(self)

    def updateSensor(self, address, level=None):
        with self.sensorlock:
            if address not in self.sensors:
                self.sensors[address] = Sensor(address)
            if level is not None:
                self.sensors[address].level = level

    def updateSwitch(self, address, thrown=None, engage=None):
        with self.switchlock:
            if address not in self.switches:
                self.switches[address] = Switch(address)
            if thrown is not None:
                self.switches[address].thrown = thrown
            if engage is not None:
                self.switches[address].engage = engage

    def getSlot(self, address):
        """
        Return the slot id associated with the loc address.

        If there is no slot known for this loc, request slot data.
        """
        for slot in self.slots:
            if slot.address == address:
                return address
        self.sendMessage(RequestLocAddress(address))
        if self.waitUntilLocAddressKnown(address):
            for slot in self.slots:
                if slot.address == address:
                    return address
        raise ValueError(f"Loc address {address} unknown")

    def getSwitchState(self, id):
        """
        Return the state of the switch.

        if the switch is unknown, request the status.
        """
        if type(id) != int:
            raise TypeError("Switch id must be an int")
        if id not in self.switches:
            self.sendMessage(RequestSwitchState(id))
            if not self.waitUntilSwitchKnown(id):
                raise ValueError("Switch id {id} unknown")
        return self.switches[id].thrown

    def getSensorState(self, id):
        """
        Return the state of the sensor.

        if the sensor is unknown, request the status.
        """
        if type(id) != int:
            raise TypeError("Sensor id must be an int")
        if id not in self.sensors:
            self.sendMessage(
                SensorState(id)
            )  # request for sensor state is same a sensor state report
            if not self.waitUntilSensorKnown(id):
                raise ValueError(f"Sensor id {id} unknown")
        return self.sensors[id].level

    def sendMessage(self, message):
        """
        place a message in the output queue of the interface.
        """
        self.interface.sendMessage(message)

    def waitUntilSwitchKnown(self, id, timeout=30):
        time_elapsed = 0
        while id not in self.switches:
            sleep(0.25)
            time_elapsed += 0.25
            if time_elapsed > timeout:
                return False
        return True

    def waitUntilSensorKnown(self, id, timeout=30):
        time_elapsed = 0
        while id not in self.sensors:
            sleep(0.25)
            time_elapsed += 0.25
            if time_elapsed > timeout:
                return False
        return True

    def waitUntilLocAddressKnown(self, address, timeout=30):
        time_elapsed = 0
        while not any(slot.address == address for slot in self.slots):
            sleep(0.25)
            time_elapsed += 0.25
            if time_elapsed > timeout:
                return False
        return True

    def __str__(self):
        newline = "\n"
        tab = "\t"
        return f"""
Scrollkeeper [{datetime.now():%H:%M:%S}]

Slots:
{newline.join(tab+str(self.slots[s]) for s in sorted(s for s in self.slots)) if len(self.slots) else tab+'<none>'}

Switches:
{newline.join(tab+str(self.switches[s]) for s in sorted(s for s in self.switches)) if len(self.switches) else tab+'<none>'}

Sensors:
{newline.join(tab+str(self.sensors[s]) for s in sorted(s for s in self.sensors)) if len(self.sensors) else tab+'<none>'}
"""
