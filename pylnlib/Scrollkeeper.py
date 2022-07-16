# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220716125748

from datetime import datetime
from threading import Lock
from time import sleep

from .Message import (
    FunctionGroup1,
    FunctionGroup2,
    FunctionGroup3,
    FunctionGroupSound,
    MoveSlots,
    RequestLocAddress,
    RequestSlotData,
    RequestSwitchFunction,
    RequestSwitchState,
    SensorState,
    SlotDataReturn,
    SlotSpeed,
    SwitchState,
)
from .Sensor import Sensor
from .Slot import Slot
from .Switch import Switch
from .Throttle import Throttle


class Scrollkeeper:
    def __init__(self, interface, slottrace=False):
        """
        A Scrollkeeper instance keeps track of the state of slots, sensors and switches.

        A Scrollkeeper instance uses information sent to its messageListener method to keep track of changes to slots, sensors and switches.
        If it receives messages for which it does not have a Slot, Sensor or Switch instance, it will send requests to get this information.

        Args:
            interface (Interface): used to send a message if no information on a particular item is present.
            slottrace (bool, optional): log every internal update to the console. Defaults to False.
        """
        self.interface = interface
        self.slottrace = slottrace
        self.slots = {}
        self.slotlock = Lock()
        self.switches = {}
        self.switchlock = Lock()
        self.sensors = {}
        self.sensorlock = Lock()
        self.dummy = False

    def messageListener(self, msg) -> None:
        """
        Handles incoming messages and updates internal state.

        If information refering an unknown slot comes in, it will issue a slot status request.

        Args:
            msg (Message): An instance of a (subclass of a) Message.
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
        elif isinstance(msg, FunctionGroup3):
            if msg.slot not in self.slots:
                self.sendMessage(RequestSlotData(msg.slot))
            else:
                if msg.fiegroup == 0x5:
                    self.updateSlot(msg.slot, f12=msg.f12, f20=msg.f20, f28=msg.f28)
                elif msg.fiegroup == 0x8:
                    self.updateSlot(
                        msg.slot,
                        f13=msg.f13,
                        f14=msg.f14,
                        f15=msg.f15,
                        f16=msg.f16,
                        f17=msg.f17,
                        f18=msg.f18,
                        f19=msg.f19,
                    )
                elif msg.fiegroup == 0x9:
                    self.updateSlot(
                        msg.slot,
                        f21=msg.f21,
                        f22=msg.f22,
                        f23=msg.f23,
                        f24=msg.f24,
                        f25=msg.f25,
                        f26=msg.f26,
                        f27=msg.f27,
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
        elif isinstance(msg, RequestSwitchFunction):
            self.updateSwitch(msg.address, msg.thrown, msg.engage)

    def updateSlot(self, id, **kwargs) -> None:
        """
        Update attributes of a slot.

        The method is thread safe.

        Args:
            id (int): The slot id.
        """
        with self.slotlock:
            if id not in self.slots:
                self.slots[id] = Slot(id)

            slot = self.slots[id]
            slot.slot = id

            for attr, val in kwargs.items():
                if dir is not None:
                    setattr(self, attr, val)
            if self.slottrace:
                print(self)

    def updateSensor(self, address, level=None) -> None:
        """
        Update the attributes of a sensor.

        The method is thread safe.

        Args:
            address (int): The address of the sensor. This is zero based.
            level (bool, optional): Either True (on) or False (off). Defaults to None.
        """
        with self.sensorlock:
            if address not in self.sensors:
                self.sensors[address] = Sensor(address)
            if level is not None:
                self.sensors[address].state = level
            if self.slottrace:
                print(self)

    def updateSwitch(self, address, thrown=None, engage=None):
        """
        update the status of a switch.

        The method is thread safe.

        Args:
            address (int): The address of the switch. This is zero based.
            thrown (bool, optional): direction of the switch. True (thrown, aka Open) or False (closed). Defaults to None.
            engage (bool, optional): whether the servo is engaged. Defaults to None.
        """
        with self.switchlock:
            if address not in self.switches:
                self.switches[address] = Switch(address)
            if thrown is not None:
                self.switches[address].thrown = thrown
            if engage is not None:
                self.switches[address].engage = engage
            if self.slottrace:
                print(self)

    def getLocoSlot(self, address):
        """
        Return the slot id associated with the loc address.

        If there is no slot known for this loc, request slot data.

        Args:
            address (int): loc address

        Raises:
            ValueError: if no slot data is available for this loc address

        Returns:
            Slot: The Slot instance associated with this loc address.
        """
        for slot in self.slots:
            if slot.address == address:
                return slot
        if self.dummy:
            return Slot(id=100, dir=0, speed=0, status=0, address=address)
        self.sendMessage(RequestLocAddress(address))
        if self.waitUntilLocAddressKnown(address):
            for slot in self.slots:
                if slot.address == address:
                    return slot
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

    def acquireSlot(self, slot):
        self.sendMessage(MoveSlots(src=slot.id, dst=slot.id))
        # TODO: ? should we wait for slot data ?

    def getThrottle(self, locaddress):
        slot = self.getLocoSlot(locaddress)
        self.acquireSlot(slot)
        return Throttle(self, locaddress)

    def getSlot(self, id):
        return self.slots[id]

    def getSensor(self, id):
        return self.sensors[id]

    def getSwitch(self, id):
        return self.switches[id]

    def getSlotIds(self):
        return [s for s in self.slots]

    def getSensorIds(self):
        return [s for s in self.sensors]

    def getSwitchIds(self):
        return [s for s in self.switches]

    def getAllStatusInfo(self):
        return {
            "slots": [self.slots[s].toJSON() for s in sorted(s for s in self.slots)],
            "switches": [
                self.switches[s].toJSON() for s in sorted(s for s in self.switches)
            ],
            "sensors": [
                self.sensors[s].toJSON() for s in sorted(s for s in self.sensors)
            ],
        }

    def __str__(self):
        newline = "\n"
        tab = "\t"
        return f"""\033[2J\033[H
Scrollkeeper [{datetime.now():%H:%M:%S}]

Slots:
{newline.join(tab+str(self.slots[s]) for s in sorted(s for s in self.slots)) if len(self.slots) else tab+'<none>'}

Switches:
{newline.join(tab+str(self.switches[s]) for s in sorted(s for s in self.switches)) if len(self.switches) else tab+'<none>'}

Sensors:
{newline.join(tab+str(self.sensors[s]) for s in sorted(s for s in self.sensors)) if len(self.sensors) else tab+'<none>'}
"""
