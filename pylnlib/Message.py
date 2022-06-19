# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220619173353


class Message:
    def __init__(self, data):
        self.opcode = data[0]
        self.length = Message.length(data[0], data[1])
        self.data = data
        self.checksum = data[-1]
        if len(data) != self.length:
            raise ValueError("length mismatch")
        if self.checksum and self.checksum != Message.checksum(data[:-1]):
            raise ValueError("checksum error")

    def __str__(self):
        return f"{self.__class__.__name__}(opcode={hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"

    def updateChecksum(self):
        self.checksum = self.data[-1] = Message.checksum(self.data[:-1])

    @staticmethod
    def length(opcode, nextbyte):
        d6d5 = (opcode >> 5) & 3
        if d6d5 == 0:
            return 2
        elif d6d5 == 1:
            return 4
        elif d6d5 == 2:
            return 6
        else:
            return int(nextbyte)

    @staticmethod
    def from_data(data):
        opcode = data[0]
        if opcode == 0x83:
            return PowerOn(data)
        elif opcode == 0x82:
            return PowerOff(data)
        elif opcode == 0xA1:
            return FunctionGroup1(data)
        elif opcode == 0xB0:
            return SwitchState(data)
        elif opcode == 0xB2:
            return SensorState(data)
        elif opcode == 0xBB:
            return RequestSlotData(data)
        elif opcode == 0xE7:
            return SlotDataReturn(data)
        return Unknown(data)

    @staticmethod
    def checksum(msg):
        chksum = 0
        for c in msg:
            chksum = chksum ^ (c ^ 0xFF)
        return chksum

    @staticmethod
    def sensoraddress(d0, d1):
        return ((d0 & 0x7F) << 1) | ((d1 & 0x0F) << 8) | ((d1 >> 5) & 0x1)

    @staticmethod
    def switchaddress(d0, d1):
        return (d0 & 0x7F) | ((d1 & 0x0F) << 7)

    @staticmethod
    def slotaddress(d0, d1):
        return (d0 & 0x7F) | ((d1 & 0x0F) << 7)


class Unknown(Message):
    pass


class PowerOn(Message):
    pass


class PowerOff(Message):
    pass


class FunctionGroup1(Message):
    def __init__(self, data):
        super().__init__(data)
        self.slot = int(data[1])
        self.dir = bool(data[2] & 0x20)
        self.f0 = bool(data[2] & 0x10)
        self.f1 = bool(data[2] & 0x1)
        self.f2 = bool(data[2] & 0x2)
        self.f3 = bool(data[2] & 0x4)
        self.f4 = bool(data[2] & 0x8)

    def __str__(self):
        return f"{self.__class__.__name__}({self.slot=} {self.dir=} {self.f0=}  {self.f1=} {self.f2=} {self.f3=} {self.f4=}| op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"


class SwitchState(Message):
    def __init__(self, data):
        super().__init__(data)
        self.address = Message.switchaddress(data[1], data[2])
        self.thrown = bool(data[2] & 0x20)
        self.engage = bool(data[2] & 0x10)

    def __str__(self):
        return f"{self.__class__.__name__}(addr={self.address+1} = {self.thrown=} {self.engage=} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"


class SensorState(Message):
    def __init__(self, data):
        super().__init__(data)
        self.address = Message.sensoraddress(data[1], data[2])
        self.level = bool(data[2] & 0x10)

    def __str__(self):
        return f"{self.__class__.__name__}(addr={self.address+1} = {'ON' if self.level else 'OFF'} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"


class RequestSlotData(Message):
    def __init__(self, slot):
        if type(slot) == int:
            data = bytearray(4)
            data[0] = 0xBB
            data[1] = self.slot = slot
            data[2] = 0
            super().__init__(data)
            self.updateChecksum()
        else:
            super().__init__(data)
            self.slot = int(data[1])

    def __str__(self):
        return f"{self.__class__.__name__}(slot = {self.slot} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"


class SlotDataReturn(Message):
    def __init__(self, data):
        super().__init__(data)
        # data[1] is always 0x0e
        self.slot = int(data[2])
        self.stat = data[3]
        self.address = Message.slotaddress(data[4], data[9])
        self.speed = int(data[5])
        self.dir = bool(data[6] & 0x20)
        self.f0 = bool(data[6] & 0x10)
        self.f1 = bool(data[6] & 0x1)
        self.f2 = bool(data[6] & 0x2)
        self.f3 = bool(data[6] & 0x4)
        self.f4 = bool(data[6] & 0x8)
        self.f5 = bool(data[10] & 0x1)
        self.f6 = bool(data[10] & 0x2)
        self.f7 = bool(data[10] & 0x4)
        self.f8 = bool(data[10] & 0x8)
        self.trk = data[7]
        self.ss2 = data[8]
        self.id1 = data[11]
        self.id2 = data[12]

    def __str__(self):
        return f"{self.__class__.__name__}(slot={self.slot} loc={self.addr} {self.dir=} {self.f0=} {self.f1=} {self.f2=} {self.f3=} {self.f4=}  {self.f5=} {self.f6=} {self.f7=} {self.f8=} {self.trk=} {self.ss2=} {self.id1=} {self.id2=}| op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"
