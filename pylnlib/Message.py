# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220801163148

# Based on LocoNet® Personal Use Edition 1.0 SPECIFICATION
# Which is © Digitrax Inc.
# See also: https://www.digitrax.com/static/apps/cms/media/documents/loconet/loconetpersonaledition.pdf
# See also: https://wiki.rocrail.net/doku.php?id=loconet:ln-pe-en

from datetime import time


class Message:
    """
    Initialize a Loconet message from a byte array.

    Represents a basic LocoNet message.
    Several subclasses are provided to implemented actual messages.

    The 'opcode' (message type) is determined from byte 0,
    The length of the data (incl. the checksum) is determined by bits in the first byte and the second byte (if it is a variable byte message)
    The checksum is the last byte in the data. If the last byte in the data is 0, no check is done, so you can create a message from scratch and calculate the checksum later.

    Args:
        data (bytearray): the bytes of the message

    Raises:
        ValueError: If the length of the byte array does not match the encoded length, a ValueError is raised.
        ValueError: If the calculated checksum doesn match the last byte of the byte array, a ValueError is raised (unless the last data byte is 0)
    """

    OPC_GPON = 0x83
    OPC_GPOFF = 0x82

    OPC_LOCO_SPD = 0xA0
    OPC_LOCO_DIRF = 0xA1
    OPC_LOCO_SND = 0xA2
    OPC_LOCO_F2 = 0xA3  # not defined in locnet specs, but implemented nevertheless
    OPC_SW_REQ = 0xB0
    OPC_SW_REP = 0xB1
    OPC_INPUT_REP = 0xB2
    OPC_LONG_ACK = 0xB4
    OPC_SLOT_STAT1 = 0xB5  # not implemented
    OPC_CONSIST_FUNC = 0xB6  # not implemented
    OPC_UNLINK_SLOTS = 0xB8  # not implemented
    OPC_LINK_SLOTS = 0xB9  # not implemented
    OPC_MOVE_SLOTS = 0xBA
    OPC_RQ_SL_DATA = 0xBB
    OPC_SW_STATE = 0xBC
    OPC_SW_ACK = 0xBD
    OPC_LOCO_ADR = 0xBF
    OPC_LOCO_F3 = 0xD4  # not defined in locnet specs, but implemented nevertheless (seen on Roco WLAN maus)
    OPC_SL_RD_DATA = 0xE7
    OPC_WR_SL_DATA = 0xEF

    def __init__(self, data):
        self.opcode = data[0]
        self.length = Message.length(data[0], data[1])
        self.data = data
        self.checksum = data[-1]
        if len(data) != self.length:
            raise ValueError("length mismatch")
        calculated_checksum = Message.checksum(data[:-1])
        if self.checksum and self.checksum != calculated_checksum:
            raise ValueError(
                f"checksum error {self.checksum:x} != {calculated_checksum=:x}"
            )

    def hexdata(self):
        """
        Return the message data as a list of numbers formatted as hexadecimals with 2 digits and without 0x prefix.

        Returns:
            list[str] :  a list of lowercase hexadecimal number with leading zeros.
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

        The length is inclusive the opcode and the final checksum.

        Args:
            opcode (byte): the opcode
            nextbyte (byte): the total number of bytes in the message if the opcode indicates this is a variable length message.

        Returns:
            _type_: _description_

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

        Args:
            data (bytearray) : the bytes of the message

        Returns:
            Message : a subclass of [Message](pylnlib.Message.md)

        !!! todo
            not all possible opcodes/message types are implemented yet.
        """
        opcode = data[0]
        if opcode == 0x83:
            return PowerOn(data)
        elif opcode == 0x82:
            return PowerOff(data)
        elif opcode == Message.OPC_LOCO_SPD:
            return SlotSpeed(data)
        elif opcode == Message.OPC_LOCO_DIRF:
            return FunctionGroup1(data)
        elif opcode == Message.OPC_LOCO_SND:
            return FunctionGroupSound(data)
        elif opcode == Message.OPC_LOCO_F2:
            return FunctionGroup2(data)
        elif opcode == 0xD4:
            return FunctionGroup3(data)
        elif opcode == 0xB0:
            return RequestSwitchFunction(data)
        elif opcode == 0xB1:
            return SwitchState(data)
        elif opcode == 0xB2:
            return SensorState(data)
        elif opcode == 0xB4:
            return LongAcknowledge(data)
        elif opcode == 0xBA:
            return MoveSlots(data)
        elif opcode == 0xBB:
            return RequestSlotData(data)
        elif opcode == 0xBC:
            return RequestSwitchState(data)
        elif opcode == 0xC0:
            return CaptureTimeStamp(data)
        elif opcode == 0xBF:
            return RequestLocAddress(data)
        elif opcode == 0xE7:
            return SlotDataReturn(data)
        elif opcode == 0xEF:
            return WriteSlotData(data)
        return Unknown(data)

    @staticmethod
    def checksum(msg):
        """
        Calculate the checksum over the message.

        The checksum is calculated over all bytes.

        This method does NOT overwrite the checksum byte, but simply returns it.

        Args:
            msg (bytes) : the data

        Returns:
            byte : the checksum over all the bytes
        """
        chksum = 0
        for c in msg:
            chksum = chksum ^ (c ^ 0xFF)
        return chksum

    @staticmethod
    def sensoraddress(d0, d1):
        """
        Return a 12-bit sensor address from the data.

        Sensors start from zero (but may typically displayed with an added offset of 1).

        Args:
            d0 (byte) : first byte of the sensor address
            d1 (byte) : second byte of the sensor address

        !!! note
            sensor addresses are 12 bits running from 11 (most significant) to 0 (least significant)
            bits 11 - 8  and bit 0 are encoded in byte d1, bits 7 - 1 in byte d0.
        """
        return ((d0 & 0x7F) << 1) | ((d1 & 0x0F) << 8) | ((d1 >> 5) & 0x1)

    @staticmethod
    def switchaddress(d0, d1):
        """
        Return an 11-bit switch address from the data.

        Switches start from zero (but may typically displayed with an added offset of 1).

        Args:
            d0 (byte) : first byte of the switch address
            d1 (byte) : second byte of the switch address

        !!! note
            switch addresses are 11 bits running from 10 (most significant) to 0 (least significant)
            bits 10 - 7 are encoded in byte d1, bits 6 - 0 in byte d0.
        """
        return (d0 & 0x7F) | ((d1 & 0x0F) << 7)

    @staticmethod
    def slotaddress(d0, d1):
        """
        Return an 11-bit slot address from the data.

        Slots start from zero (but slot 0 is special, as are several others >= 0x70).

        Args:
            d0 (byte) : first byte of the switch address
            d1 (byte) : second byte of the switch address

        !!! note
            slot addresses are 11 bits running from 10 (most significant) to 0 (least significant)
            bits 10 - 7 are encoded in byte d1, bits 6 - 0 in byte d0.

        !!! note
            all addresses > 111 are considered special and not used for locos.
        """
        return (d0 & 0x7F) | ((d1 & 0x0F) << 7)


class Unknown(Message):
    """
    An Unknown message simply holds the data bytes.
    """

    pass


class PowerOn(Message):
    """
    A PowerOn message represents a global track power on message.

    Args:
        data (bytes, optional): raw message data. Defaults to None.
    """

    def __init__(self, data=None):
        if data is None:
            super().__init__(bytearray([Message.OPC_GPON, 0]))
            self.updateChecksum()
        else:
            super().__init__(data)


class PowerOff(Message):
    """
    A PowerOff message represents a global track power off message.

    Args:
        data (bytes, optional): raw message data. Defaults to None.
    """

    def __init__(self, data=None):
        if data is None:
            super().__init__(bytearray([Message.OPC_GPOFF, 0]))
            self.updateChecksum()
        else:
            super().__init__(data)


class FunctionGroup1(Message):
    """
    A FunctionGroup1 message represents a slot function status change.

    It holds the status for the direction and functions f0 - f4.

    Args:
        data (bytes, optional): raw message data. Defaults to None.
        slot (int, optional): slot number. Defaults to None.
        dir (bool, optional): running direction. Defaults to None.
        f0 (bool, optional): function 0 (running lights). Defaults to None.
        f1 (bool, optional): function 1 (engine sound). Defaults to None.
        f2 (bool, optional): function 2 (whistle). Defaults to None.
        f3 (bool, optional): function 3. Defaults to None.
        f4 (bool, optional): function 4. Defaults to None.

    Raises:
        ValueError: if data is specified at the same time as one of the other arguments.
    """

    def __init__(
        self,
        data=None,
        slot=None,
        dir=None,
        f0=None,
        f1=None,
        f2=None,
        f3=None,
        f4=None,
    ):
        if data is None:
            self.slot = slot
            self.dir = dir
            self.f0 = f0
            self.f1 = f1
            self.f2 = f2
            self.f3 = f3
            self.f4 = f4
            data = bytearray(4)
            data[0] = Message.OPC_LOCO_DIRF
            data[1] = self.slot
            data[2] = 0
            data[2] += 0x20 if self.dir else 0
            data[2] += 0x10 if self.f0 else 0
            data[2] += 0x1 if self.f1 else 0
            data[2] += 0x2 if self.f2 else 0
            data[2] += 0x4 if self.f3 else 0
            data[2] += 0x8 if self.f4 else 0
            super().__init__(data)
            self.updateChecksum()
        else:
            if dir is not None or f0 is not None:
                raise ValueError(
                    "slot and speed arguments cannot be combined with data argument"
                )
            super().__init__(data)
            self.slot = int(data[1])
            self.dir = bool(data[2] & 0x20)
            self.f0 = bool(data[2] & 0x10)
            self.f1 = bool(data[2] & 0x1)
            self.f2 = bool(data[2] & 0x2)
            self.f3 = bool(data[2] & 0x4)
            self.f4 = bool(data[2] & 0x8)

    def __str__(self):
        return f"{self.__class__.__name__}(slot = {self.slot} dir: {self.dir} f0: {self.f0}  f1: {self.f1} f2: {self.f2} f3: {self.f3} f4: {self.f4} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"


class FunctionGroupSound(Message):
    """
    A FunctionGroupSound message represents a slot function status change.

    It holds the status for functions f5 - f8.

    Args:
        data (bytes, optional): raw message data. Defaults to None.
        slot (int, optional): slot number. Defaults to None.
        f5 (bool, optional): function 5. Defaults to None.
        f6 (bool, optional): function 6. Defaults to None.
        f7 (bool, optional): function 7. Defaults to None.
        f8 (bool, optional): function 8. Defaults to None.

    Raises:
        ValueError:  if data is specified at the same time as one of the other arguments.

    """

    def __init__(self, data=None, slot=None, f5=None, f6=None, f7=None, f8=None):
        if data is None:
            self.slot = slot
            self.f5 = f5
            self.f6 = f6
            self.f7 = f7
            self.f8 = f8
            data = bytearray(4)
            data[0] = Message.OPC_LOCO_SND
            data[1] = self.slot
            data[2] = 0
            data[2] += 0x1 if self.f5 else 0
            data[2] += 0x2 if self.f6 else 0
            data[2] += 0x4 if self.f7 else 0
            data[2] += 0x8 if self.f8 else 0
            super().__init__(data)
            self.updateChecksum()
        else:
            if slot is not None or f5 is not None:
                raise ValueError(
                    "slot and function arguments cannot be combined with data argument"
                )
            super().__init__(data)
            self.slot = int(data[1])
            self.f5 = bool(data[2] & 0x1)
            self.f6 = bool(data[2] & 0x2)
            self.f7 = bool(data[2] & 0x4)
            self.f8 = bool(data[2] & 0x8)

    def __str__(self):
        return f"{self.__class__.__name__}(slot = {self.slot} f5: {self.f5}  f6: {self.f6} f7: {self.f7} f8: {self.f8} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"


class FunctionGroup2(Message):
    """
    A FunctionGroup2 message represents a slot function status change.

    It holds the status for functions f9 - f12.

    Args:
        data (bytes, optional): raw message data. Defaults to None.
        slot (int, optional): slot number. Defaults to None.
        f9 (bool, optional): function 9. Defaults to None.
        f10 (bool, optional): function 10. Defaults to None.
        f11 (bool, optional): function 11. Defaults to None.
        f12 (bool, optional): function 12. Defaults to None.

    Raises:
        ValueError:  if data is specified at the same time as one of the other arguments.
    """

    def __init__(self, data=None, slot=None, f9=None, f10=None, f11=None, f12=None):
        if data is None:
            self.slot = slot
            self.f9 = f9
            self.f10 = f10
            self.f11 = f11
            self.f12 = f12
            data = bytearray(4)
            data[0] = Message.OPC_LOCO_F2
            data[1] = self.slot
            data[2] = 0
            data[2] += 0x1 if self.f9 else 0
            data[2] += 0x2 if self.f10 else 0
            data[2] += 0x4 if self.f11 else 0
            data[2] += 0x8 if self.f12 else 0
            super().__init__(data)
            self.updateChecksum()
        else:
            if slot is not None or f9 is not None:
                raise ValueError(
                    "slot and function arguments cannot be combined with data argument"
                )
            super().__init__(data)
            self.slot = int(data[1])
            self.f9 = bool(data[2] & 0x1)
            self.f10 = bool(data[2] & 0x2)
            self.f11 = bool(data[2] & 0x4)
            self.f12 = bool(data[2] & 0x8)

    def __str__(self):
        return f"{self.__class__.__name__}(slot = {self.slot} f9: {self.f9}  f10: {self.f10} f11: {self.f11} f12: {self.f12} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"


class FunctionGroup3(Message):
    """
    A FunctionGroup3 message represents a slot function status change.

    Depending on the fiegroup, it holds the status for functions f13 - f19, f21 - f27 or f12 + f20 +f28.

    Other Parameters:
        f13 (bool, optional): function 13. Defaults to None.
        f14 (bool, optional): function 14. Defaults to None.
        f15 (bool, optional): function 15. Defaults to None.
        f16 (bool, optional): function 16. Defaults to None.
        f17 (bool, optional): function 17. Defaults to None.
        f18 (bool, optional): function 18. Defaults to None.
        f19 (bool, optional): function 19. Defaults to None.
        f21 (bool, optional): function 21. Defaults to None.
        f22 (bool, optional): function 22. Defaults to None.
        f23 (bool, optional): function 23. Defaults to None.
        f24 (bool, optional): function 24. Defaults to None.
        f25 (bool, optional): function 25. Defaults to None.
        f26 (bool, optional): function 26. Defaults to None.
        f27 (bool, optional): function 27. Defaults to None.
        f12 (bool, optional): function 12. Defaults to None.
        f20 (bool, optional): function 20. Defaults to None.
        f28 (bool, optional): function 28. Defaults to None.

    Raises:
        ValueError:  if data is specified at the same time as one of the other arguments.
        ValueError:  if an unknown argument is passed.
        ValueError:  if arguments from different function groups are passed at the same time.
    """

    params = {
        "f12",
        "f13",
        "f14",
        "f15",
        "f16",
        "f17",
        "f18",
        "f19",
        "f20",
        "f21",
        "f22",
        "f23",
        "f24",
        "f25",
        "f26",
        "f27",
        "f28",
    }
    p12 = {"f12", "f20", "f28"}
    p13 = {"f13", "f14", "f15", "f16", "f17", "f18", "f19"}
    p21 = {"f21", "f22", "f23", "f24", "f25", "f26", "f27"}

    def __init__(self, data=None, slot=None, **kwargs):
        if data is None:
            self.slot = slot
            for k in FunctionGroup3.params:
                setattr(self, k, False)
            for k, v in kwargs.items():
                if k in FunctionGroup3.params:
                    setattr(self, k, v)
                else:
                    raise ValueError(f"unknown parameter {k}")
            if (
                sum(
                    [
                        bool(set(kwargs.keys()) & s)
                        for s in (
                            FunctionGroup3.p12,
                            FunctionGroup3.p13,
                            FunctionGroup3.p21,
                        )
                    ]
                )
                != 1
            ):
                raise ValueError(f"mixed param groups")
            data = bytearray(6)
            data[0] = Message.OPC_LOCO_F3
            data[1] = 0x20
            data[2] = self.slot
            if "f13" in kwargs:
                data[3] = 0x08
                data[4] = 0
                if self.f13:
                    data[4] += 0x1
                if self.f14:
                    data[4] += 0x2
                if self.f15:
                    data[4] += 0x4
                if self.f16:
                    data[4] += 0x8
                if self.f17:
                    data[4] += 0x10
                if self.f18:
                    data[4] += 0x20
                if self.f19:
                    data[4] += 0x40
            elif "f21" in kwargs:
                data[3] = 0x09
                data[4] = 0
                if self.f21:
                    data[4] += 0x1
                if self.f22:
                    data[4] += 0x2
                if self.f23:
                    data[4] += 0x4
                if self.f24:
                    data[4] += 0x8
                if self.f25:
                    data[4] += 0x10
                if self.f26:
                    data[4] += 0x20
                if self.f27:
                    data[4] += 0x40
            elif "f12" in kwargs:
                data[3] = 0x05
                data[4] = 0
                if self.f12:
                    data[4] += 0x10
                if self.f20:
                    data[4] += 0x20
                if self.f28:
                    data[4] += 0x40
            self.fiegroup = data[3]
            super().__init__(data)
            self.updateChecksum()
        else:
            if slot is not None or len(kwargs):
                raise ValueError(
                    "slot and function arguments cannot be combined with data argument"
                )
            super().__init__(data)
            # data[1] is always 0x20
            self.slot = int(data[2])
            self.fiegroup = data[3]
            if self.fiegroup == 0x08:
                self.f13 = bool(data[4] & 0x1)
                self.f14 = bool(data[4] & 0x2)
                self.f15 = bool(data[4] & 0x4)
                self.f16 = bool(data[4] & 0x8)
                self.f17 = bool(data[4] & 0x10)
                self.f18 = bool(data[4] & 0x20)
                self.f19 = bool(data[4] & 0x40)
            elif self.fiegroup == 0x09:
                self.f21 = bool(data[4] & 0x1)
                self.f22 = bool(data[4] & 0x2)
                self.f23 = bool(data[4] & 0x4)
                self.f24 = bool(data[4] & 0x8)
                self.f25 = bool(data[4] & 0x10)
                self.f26 = bool(data[4] & 0x20)
                self.f27 = bool(data[4] & 0x40)
            elif self.fiegroup == 0x05:
                self.f12 = bool(data[4] & 0x10)
                self.f20 = bool(data[4] & 0x20)
                self.f28 = bool(data[4] & 0x40)

    def __str__(self):
        if self.fiegroup == 0x05:
            return f"{self.__class__.__name__}(slot = {self.slot} f12: {self.f12}  f20: {self.f20} f28: {self.f28} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"
        elif self.fiegroup == 0x08:
            return f"{self.__class__.__name__}(slot = {self.slot} f13: {self.f13}  f14: {self.f14} f15: {self.f15} f16: {self.f16} f17: {self.f17} f18: {self.f18} f19: {self.f19} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"
        elif self.fiegroup == 0x09:
            return f"{self.__class__.__name__}(slot = {self.slot} f21: {self.f21}  f22: {self.f22} f23: {self.f23} f24: {self.f24} f25: {self.f25} f26: {self.f26} f27: {self.f27} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"
        else:
            return f"{self.__class__.__name__}(slot = {self.slot} fiegroup: {self.fiegroup} | op = {hex(self.opcode)}, {self.length=}, data={list(map(hex,map(int, self.data)))})"


class RequestSwitchFunction(Message):
    """
    A RequestSwitchFunction message represents a request for a switch status change.

    It holds the info on whether the switch should be closed or thrown,
    as well as whether the switch motor should be engaged.

    Args:
        data (bytearray(4) or int): either 4 bytes of raw data or the switch address
        thrown (bool, optional): if a switch address is given, this should hold thrown or closed. Defaults to None.
        engage (bool, optional): if a switch address is given, this should signal whether the motor should be engaged . Defaults to None.
    """

    def __init__(self, data, thrown=None, engage=None):
        if type(data) == int:
            self.address = data
            data = bytearray(4)
            self.opcode = data[0] = Message.OPC_SW_REQ
            self.thrown = thrown
            self.engage = engage
            data[1] = self.address & 0x7F
            data[2] = self.address >> 7
            if not self.thrown:
                data[2] |= 0x20
            if self.engage:
                data[2] |= 0x10
            super().__init__(data)
            self.updateChecksum()
        else:
            super().__init__(data)
            self.address = Message.switchaddress(data[1], data[2])
            self.thrown = bool(data[2] & 0x20)
            self.engage = bool(data[2] & 0x10)

    def __str__(self):
        return f"{self.__class__.__name__}(addr={self.address+1:2d} = {self.thrown=} {self.engage=} | op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"


class SwitchState(Message):
    """
    A SwitchState message represents a switch status.

    It holds the info on whether the switch is closed or thrown,
    as well as whether the switch motor is engaged.

    Args:
        data (bytearray(4) or int): either 4 bytes of raw data or the switch address
        thrown (bool, optional): if a switch address is given, this should hold thrown or closed. Defaults to None.
        engage (bool, optional): if a switch address is given, this should signal whether the motor should be engaged . Defaults to None.
    """

    def __init__(self, id, thrown=None, engage=None):
        if type(id) == int:
            data = bytearray(4)
            data[0] = 0xB1
            self.address = id
            self.thrown = thrown
            self.engage = engage
            data[1] = id & 0x7F
            data[2] = id >> 7
            data[2] |= 0x20 if thrown else 0
            data[2] |= 0x10 if engage else 0
            super().__init__(data)
            self.updateChecksum()
        else:
            super().__init__(id)
            self.address = Message.switchaddress(id[1], id[2])
            self.thrown = bool(id[2] & 0x20)
            self.engage = bool(id[2] & 0x10)

    def __str__(self):
        return f"{self.__class__.__name__}(addr={self.address+1:2d} = {self.thrown=} {self.engage=} | op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"


class RequestSwitchState(Message):
    """
    A RequestSwitchState message represents a request for a switch status update.

    Args:
        data (bytearray(4) or int): either 4 bytes of raw data or the switch address
    """

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
    """
    A SensorState message represents a sensor's status.

    It holds the info on whether the sensor is on or off.

    Args:
        id (bytearray(4) or int): either 4 bytes of raw data or the switch address
        level (bool, optional): if a sensor address is given, this should hold True or False. Defaults to None.
    """

    def __init__(self, id, level=None):
        if type(id) == int:
            data = bytearray(4)
            data[0] = 0xB2
            self.address = id
            self.level = level
            data[1] = (id >> 1) & 0x7F
            data[2] = (id >> 8) | (0x20 if id % 2 else 0)
            data[2] |= 0x10 if level else 0
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
        return f"{self.__class__.__name__}(slot={self.slot} loc={self.address} status: {self.status} dir: {self.dir} speed: {self.speed} f0: {self.f0} f1: {self.f1} f2: {self.f2} f3: {self.f3} f4: {self.f4}  f5: {self.f5} f6: {self.f6} f7: {self.f7} f8: {self.f8} trk: {self.trk} ss2: {self.ss2} id1: {self.id1} id2: {self.id2} | op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"


class WriteSlotData(SlotDataReturn):
    def __init__(self, slot):
        if isinstance(slot, bytes) or isinstance(slot, bytearray):
            super().__init__(slot)
        else:
            data = bytearray(14)
            data[0] = 0xEF
            data[1] = 0x0E
            data[2] = slot.id
            data[3] = slot.status
            data[4] = slot.address & 0x7F
            data[9] = slot.address >> 7
            data[5] = slot.speed
            data[6] = 0
            data[6] += 0x20 if slot.dir else 0
            data[6] += 0x10 if slot.f0 else 0
            data[6] += 0x1 if slot.f1 else 0
            data[6] += 0x2 if slot.f2 else 0
            data[6] += 0x4 if slot.f3 else 0
            data[6] += 0x8 if slot.f4 else 0
            data[7] = data[8] = 0
            data[7] += slot.trk if slot.trk else 0
            data[8] += slot.ss2 if slot.ss2 else 0
            data[10] = 0
            data[10] += 0x1 if slot.f5 else 0
            data[10] += 0x2 if slot.f6 else 0
            data[10] += 0x4 if slot.f7 else 0
            data[10] += 0x8 if slot.f8 else 0
            data[11] = data[12] = 0
            data[11] += slot.id1 if slot.id1 else 0
            data[12] += slot.id2 if slot.id2 else 0
            Message.__init__(self, data)  # cannot skip the chain with super()
            self.updateChecksum()


class SlotSpeed(Message):
    def __init__(self, data=None, slot=None, speed=None):
        if data is None:
            self.slot = slot
            self.speed = speed
            data = bytearray(4)
            data[0] = 0xA0
            data[1] = slot
            data[2] = speed
            super().__init__(data)
            self.updateChecksum()
        else:
            if slot is not None or speed is not None:
                raise ValueError(
                    "slot and speed arguments cannot be combined with data argument"
                )
            self.slot = int(data[1])
            self.speed = data[2]
            super().__init__(data)

    def __str__(self):
        return f"{self.__class__.__name__}(slot={self.slot} speed: {self.speed} | op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"


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


class MoveSlots(Message):
    def __init__(self, data=None, src=None, dst=None):
        if data is None:
            self.src = src
            self.dst = dst
            data = bytearray(4)
            data[0] = 0xBA
            data[1] = self.src
            data[2] = self.dst
            super().__init__(data)
            self.updateChecksum()
        else:
            if src is not None or dst is not None:
                raise ValueError("slot arguments cannot be combined with data argument")
            super().__init__(data)
            self.src = int(data[1])
            self.dst = int(data[2])

    def __str__(self):
        return f"{self.__class__.__name__}(src = {self.src} dst = {self.dst}| op = {hex(self.opcode)}, {self.length=}, data={self.hexdata()})"


class CaptureTimeStamp(Message):
    def __init__(self, t):
        if isinstance(t, time):
            data = bytearray(6)
            data[0] = 0xC0
            data[1] = t.hour
            data[2] = t.minute
            data[3] = t.second
            data[4] = t.microsecond // 10000
            self.time = t
            super().__init__(data)
            self.updateChecksum()
        else:
            super().__init__(t)
            self.time = time(
                hour=t[1], minute=t[2], second=t[3], microsecond=t[4] * 10000
            )
