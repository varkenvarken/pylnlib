# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220619130959


class Message:
    def __init__(self, data):
        self.opcode = data[0]
        self.length = Message.length(data[0], data[1])
        self.data = data
        self.checksum = data[-1]
        if len(data) != self.length:
            raise ValueError("length mismatch")
        if self.checksum != Message.checksum(data[:-1]):
            raise ValueError("checksum error")

    def __str__(self):
        return f"{self.__class__.__name__}(opcode={hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"

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
        elif opcode == 0xBd:
            return SwitchState(data)
        elif opcode == 0xB2:
            return SensorState(data)
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

class Unknown(Message):
    pass


class PowerOn(Message):
    pass


class PowerOff(Message):
    pass


class SwitchState(Message):
    def __init__(self, data):
        super().__init__(data)
        self.address = Message.switchaddress(data[1], data[2])
        self.state = data[2] & 0x10
        self.direction = data[2] & 0x20 

    def __str__(self):
        return f"{self.__class__.__name__}({self.address=} = dir({self.direction}) on({self.state}) | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"



class SensorState(Message):
    def __init__(self, data):
        super().__init__(data)
        self.address = Message.sensoraddress(data[1], data[2])
        self.level = data[2] & 0x10

    def __str__(self):
        return f"{self.__class__.__name__}({self.address=} = {self.level} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"
