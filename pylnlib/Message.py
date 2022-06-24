# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220623191058

# Based on LocoNet® Personal Use Edition 1.0 SPECIFICATION
# Which is © Digitrax Inc.
# See also: https://www.digitrax.com/static/apps/cms/media/documents/loconet/loconetpersonaledition.pdf
# See also: https://wiki.rocrail.net/doku.php?id=loconet:ln-pe-en


class Message:
    """
    represents a LocoNet message.

    several subclasses are provided to implemented actual messages.
    """
    OPC_GPON = 0x83
    OPC_GPOFF = 0x82

    OPC_LOCO_SPD = 0xA0  # not implemented
    OPC_LOCO_DIRF = 0xA1
    OPC_LOCO_SND = 0xA2  # not implemented
    OPC_SW_REQ = 0xB0
    OPC_SW_REP = 0xB1  # not implemented
    OPC_INPUT_REP = 0xB2
    OPC_LONG_ACK = 0xB4
    OPC_SLOT_STAT1 = 0xB5  # not implemented
    OPC_CONSIST_FUNC = 0xB6  # not implemented
    OPC_UNLINK_SLOTS = 0xB8  # not implemented
    OPC_LINK_SLOTS = 0xB9  # not implemented
    OPC_MOVE_SLOTS = 0xBA  # not implemented
    OPC_RQ_SL_DATA = 0xBB
    OPC_SW_STATE = 0xBC
    OPC_SW_ACK = 0xBD  # not implemented
    OPC_LOCO_ADR = 0xBF
    OPC_SL_RD_DATA = 0xE7
    OPC_WR_SL_DATA = 0xEF  # not implemented

    def __init__(self, data):
        """
        Initialize a message from a byte array.

        The 'opcode' (message type) is determined from byte 0,
        The length of the data (incl. the checksum) is determined by bits in the first byte and the second byte (if it is a variable byte message)
        The checksum is the last byte in the data. If the last byte in the data is 0, no check is done, so you can create a message from scratch and calculate the checksum later.

        If the length of the byte array does not match the encoded length, a ValueError is raised.
        If the calculated checksum doesn match the last byte of the byte array, a ValueError is raised (unless the last data byte is 0)
        """
        self.opcode = data[0]
        self.length = Message.length(data[0], data[1])
        self.data = data
        self.checksum = data[-1]
        if len(data) != self.length:
            raise ValueError("length mismatch")
        if self.checksum and self.checksum != Message.checksum(data[:-1]):
            raise ValueError("checksum error")

    def hexdata(self):
        """
        Return the message data as a list of numbers formatted as hexadecimals with 2 digits and without 0x prefix.
        """
        return list(f"{v:02x}" for v in map(int, self.data))

    def __str__(self):
        return f"{self.__class__.__name__}(opcode={hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"

    def updateChecksum(self):
        """
        Calculate the checksum of the data and store it in the last byte.
        """
        self.checksum = self.data[-1] = Message.checksum(self.data[:-1])

    @staticmethod
    def length(opcode, nextbyte):
        """
        Determine the length of a LocoNet message based on its opcode and next byte.

        The next byte holds the total number of bytes in the message if the opcode indicates this is a variable length message.

        The length is inclusive the opcode and the final checksum.
        """
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
        """
        A factory method that returns a specific subclass of a Message based on the opcode, or an instance of Unknown.

        TODO: not all possible opcodes/message types are implemented yet.
        """
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
        elif opcode == 0xB4:
            return LongAcknowledge(data)
        elif opcode == 0xBB:
            return RequestSlotData(data)
        elif opcode == 0xBC:
            return RequestSwitchState(data)
        elif opcode == 0xBF:
            return RequestLocAddress(data)
        elif opcode == 0xE7:
            return SlotDataReturn(data)
        return Unknown(data)

    @staticmethod
    def checksum(msg):
        """
        Calculate the checksum over the data of a message.

        The checksum is calculate over all data bytes except the last one (which will be the checksum).

        This method does NOT overwrite the checksum byte.
        """
        chksum = 0
        for c in msg:
            chksum = chksum ^ (c ^ 0xFF)
        return chksum

    @staticmethod
    def sensoraddress(d0, d1):
        """
        Return a sensor address from the data.
        
        Sensors start from zero (but may typically displayed with an added offset of 1).
        """
        return ((d0 & 0x7F) << 1) | ((d1 & 0x0F) << 8) | ((d1 >> 5) & 0x1)

    @staticmethod
    def switchaddress(d0, d1):
        """
        Return a switch address from the data.
        
        Switches start from zero (but may typically displayed with an added offset of 1).
        """
        return ((d0 & 0x7F) << 1) | ((d1 & 0x0F) << 8) | ((d1 >> 5) & 0x1)

    @staticmethod
    def slotaddress(d0, d1):
        """
        Return a slot address from the data.
        
        Sensors start from zero (but slot 0 is special, as are several others >= 0x70).
        """
        return ((d0 & 0x7F) << 1) | ((d1 & 0x0F) << 8) | ((d1 >> 5) & 0x1)


class Unknown(Message):
    """
    An Unknown message simply hold the data bytes.
    """
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
        return f"{self.__class__.__name__}(addr={self.address+1:2d} = {self.thrown=} {self.engage=} | op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"


class RequestSwitchState(Message):
    def __init__(self, id):
        if type(id) == int:
            data = bytearray(4)
            data[0] = 0xBC
            self.address = id
            data[1] = id & 0x7F
            data[2] = id >> 7
            super().__init__(data)
            self.updateChecksum()
        else:
            super().__init__(id)
            self.address = Message.switchaddress(id[1], id[2])

    def __str__(self):
        return f"{self.__class__.__name__}(addr={self.address+1:2d} | op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"


class SensorState(Message):
    def __init__(self, id):
        if type(id) == int:
            data = bytearray(4)
            data[0] = 0xB2
            self.address = id
            data[1] = (id >> 1) & 0x7F
            data[2] = (id >> 8) | (0x10 if id % 2 else 0)
            super().__init__(data)
            self.updateChecksum()
        else:
            super().__init__(id)
            self.address = Message.sensoraddress(id[1], id[2])
            self.level = bool(id[2] & 0x10)

    def __str__(self):
        return f"{self.__class__.__name__}(addr={self.address+1:2d} = {' ON' if self.level else 'OFF'} | op = {hex(self.opcode)}, {self.length=}, data={ self.hexdata()})"


class LongAcknowledge(Message):
    def __init__(self, data):
        super().__init__(data)
        self.opcode = data[1] | 0x80
        self.ack1 = int(data[2])

    def __str__(self):
        return f"{self.__class__.__name__}(reply to opcode = {hex(self.opcode)}, ack1 = {self.ack1} | op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"


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
            super().__init__(slot)
            self.slot = int(slot[1])

    def __str__(self):
        return f"{self.__class__.__name__}(slot = {self.slot} | op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"


class SlotDataReturn(Message):
    def __init__(self, data):
        super().__init__(data)
        # data[1] is always 0x0e
        self.slot = int(data[2])
        self.status = data[3]
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
        return f"{self.__class__.__name__}(slot={self.slot} loc={self.address} {self.status=} {self.dir=} {self.speed= }{self.f0=} {self.f1=} {self.f2=} {self.f3=} {self.f4=}  {self.f5=} {self.f6=} {self.f7=} {self.f8=} {self.trk=} {self.ss2=} {self.id1=} {self.id2=}| op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"


class RequestLocAddress(Message):
    def __init__(self, address):
        if type(address) == int:
            data = bytearray(4)
            data[0] = 0xBF
            data[1] = address & 0x7F
            data[2] = address >> 7
            self.address = address
            super().__init__(data)
            self.updateChecksum()
        else:
            super().__init__(address)
            self.address = Message.slotaddress(address[1], address[2])

    def __str__(self):
        return f"{self.__class__.__name__}(address = {self.address} | op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"
