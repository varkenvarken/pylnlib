# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220803092941

# Based on LocoNet® Personal Use Edition 1.0 SPECIFICATION
# Which is © Digitrax Inc.
# See also: https://www.digitrax.com/static/apps/cms/media/documents/loconet/loconetpersonaledition.pdf
# See also: https://wiki.rocrail.net/doku.php?id=loconet:ln-pe-en


import pytest

from pylnlib.Message import (
    PowerOn,
    PowerOff,
    Message,
    FunctionGroup1,
    FunctionGroupSound,
    FunctionGroup2,
    FunctionGroup3,
    RequestSwitchFunction,
    SwitchState,
    RequestSwitchState,
    SensorState,
    LongAcknowledge,
    RequestSlotData,
    SlotDataReturn,
    WriteSlotData,
    SlotSpeed,
    RequestLocAddress,
    MoveSlots,
    CaptureTimeStamp,
    Unknown,
)

from pylnlib.Slot import Slot


class TestMessage:

    PowerOn_data = bytes([0x83, 0x7C])

    def test_PowerOn_from_data(self):
        assert type(Message.from_data(TestMessage.PowerOn_data)) == PowerOn

    def test_PowerOn_from_init(self):
        msg = PowerOn()
        assert msg.data == TestMessage.PowerOn_data

    PowerOff_data = bytes([0x82, 0x7D])

    def test_PowerOff_from_data(self):
        assert type(Message.from_data(TestMessage.PowerOff_data)) == PowerOff

    def test_PowerOff_from_init(self):
        msg = PowerOff()
        assert msg.data == TestMessage.PowerOff_data

    FunctionGroup1_data = bytes([0xA1, 0x03, 0x3F, 0x62])

    def test_FunctionGroup1_from_data(self):
        msg = Message.from_data(TestMessage.FunctionGroup1_data)
        assert type(msg) == FunctionGroup1
        assert msg.slot == 3
        assert msg.dir == True
        assert msg.f0 == True
        assert msg.f1 == True
        assert msg.f2 == True
        assert msg.f3 == True
        assert msg.f4 == True

    def test_FunctionGroup1_from_init(self):
        msg = FunctionGroup1(
            slot=3, dir=True, f0=True, f1=True, f2=True, f3=True, f4=True
        )
        assert msg.data == TestMessage.FunctionGroup1_data

    def test_FunctionGroup1_from_init_raise(self):
        with pytest.raises(ValueError):
            msg = FunctionGroup1(
                TestMessage.FunctionGroup1_data,
                slot=3,
                dir=True,
                f0=True,
                f1=True,
                f2=True,
                f3=True,
                f4=True,
            )

    FunctionGroupSound_data = bytes([0xA2, 0x03, 0x0F, 0x51])

    def test_FunctionGroupSound_from_data(self):
        msg = Message.from_data(TestMessage.FunctionGroupSound_data)
        assert type(msg) == FunctionGroupSound
        assert msg.slot == 3
        assert msg.f5 == True
        assert msg.f6 == True
        assert msg.f7 == True
        assert msg.f8 == True

    def test_FunctionGroupSound_from_init(self):
        msg = FunctionGroupSound(slot=3, f5=True, f6=True, f7=True, f8=True)
        assert msg.data == TestMessage.FunctionGroupSound_data

    def test_FunctionGroupSound_from_init_raise(self):
        with pytest.raises(ValueError):
            msg = FunctionGroupSound(
                TestMessage.FunctionGroupSound_data,
                slot=3,
                f5=True,
                f6=True,
                f7=True,
                f8=True,
            )

    FunctionGroup2_data = bytes([0xA3, 0x03, 0x0F, 0x50])

    def test_FunctionGroup2_from_data(self):
        msg = Message.from_data(TestMessage.FunctionGroup2_data)
        assert type(msg) == FunctionGroup2
        assert msg.slot == 3
        assert msg.f9 == True
        assert msg.f10 == True
        assert msg.f11 == True
        assert msg.f12 == True

    def test_FunctionGroup2_from_init(self):
        msg = FunctionGroup2(slot=3, f9=True, f10=True, f11=True, f12=True)
        assert msg.data == TestMessage.FunctionGroup2_data

    def test_FunctionGroup2_from_init_raise(self):
        with pytest.raises(ValueError):
            msg = FunctionGroup2(
                TestMessage.FunctionGroup2_data,
                slot=3,
                f9=True,
                f10=True,
                f11=True,
                f12=True,
            )

    FunctionGroup3_data_p13 = bytes([0xD4, 0x20, 0x03, 0x08, 0x7F, 0x7F])
    FunctionGroup3_data_p21 = bytes([0xD4, 0x20, 0x03, 0x09, 0x7F, 0x7E])
    FunctionGroup3_data_p12 = bytes([0xD4, 0x20, 0x03, 0x05, 0x70, 0x7D])

    def test_FunctionGroup3_from_data_p13(self):
        msg = Message.from_data(TestMessage.FunctionGroup3_data_p13)
        assert type(msg) == FunctionGroup3
        assert msg.slot == 3
        assert msg.f13 == True
        assert msg.f14 == True
        assert msg.f15 == True
        assert msg.f16 == True
        assert msg.f17 == True
        assert msg.f18 == True
        assert msg.f19 == True

    def test_FunctionGroup3_from_init_p13(self, capsys):
        msg = FunctionGroup3(
            slot=3, f13=True, f14=True, f15=True, f16=True, f17=True, f18=True, f19=True
        )
        assert msg.data == TestMessage.FunctionGroup3_data_p13
        print(msg)
        captured = capsys.readouterr()
        assert (
            captured.out
            == "FunctionGroup3(slot = 3 f13: True  f14: True f15: True f16: True f17: True f18: True f19: True | op = 0xd4, self.length=6, data=['0xd4', '0x20', '0x3', '0x8', '0x7f', '0x7f'])\n"
        )

    def test_FunctionGroup3_from_data_p21(self):
        msg = Message.from_data(TestMessage.FunctionGroup3_data_p21)
        assert type(msg) == FunctionGroup3
        assert msg.slot == 3
        assert msg.f21 == True
        assert msg.f22 == True
        assert msg.f23 == True
        assert msg.f24 == True
        assert msg.f25 == True
        assert msg.f26 == True
        assert msg.f27 == True

    def test_FunctionGroup3_from_init_p21(self, capsys):
        msg = FunctionGroup3(
            slot=3, f21=True, f22=True, f23=True, f24=True, f25=True, f26=True, f27=True
        )
        assert msg.data == TestMessage.FunctionGroup3_data_p21
        print(msg)
        captured = capsys.readouterr()
        assert (
            captured.out
            == "FunctionGroup3(slot = 3 f21: True  f22: True f23: True f24: True f25: True f26: True f27: True | op = 0xd4, self.length=6, data=['0xd4', '0x20', '0x3', '0x9', '0x7f', '0x7e'])\n"
        )

    def test_FunctionGroup3_from_data_p12(self):
        msg = Message.from_data(TestMessage.FunctionGroup3_data_p12)
        assert type(msg) == FunctionGroup3
        assert msg.slot == 3
        assert msg.f12 == True
        assert msg.f20 == True
        assert msg.f28 == True

    def test_FunctionGroup3_from_init_p12(self, capsys):
        msg = FunctionGroup3(slot=3, f12=True, f20=True, f28=True)
        assert msg.data == TestMessage.FunctionGroup3_data_p12
        print(msg)
        captured = capsys.readouterr()
        assert (
            captured.out
            == "FunctionGroup3(slot = 3 f12: True  f20: True f28: True | op = 0xd4, self.length=6, data=['0xd4', '0x20', '0x3', '0x5', '0x70', '0x7d'])\n"
        )

    def test_FunctionGroup3_from_init_punknown(self):
        with pytest.raises(ValueError):
            msg = FunctionGroup3(slot=3, f112=True, f20=True, f28=True)

    def test_FunctionGroup3_from_init_pmixed(self):
        with pytest.raises(ValueError):
            msg = FunctionGroup3(slot=3, f12=True, f13=True, f28=True)

    def test_FunctionGroup3_from_init_pmixed2(self):
        with pytest.raises(ValueError):
            msg = FunctionGroup3(
                TestMessage.FunctionGroup3_data_p13,
                slot=3,
                f12=True,
                f13=True,
                f28=True,
            )

    RequestSwitchFunction_data = bytes([0xB0, 0x03, 0x10, 0x5C])

    def test_RequestSwitchFunction_from_data(self):
        msg = RequestSwitchFunction(TestMessage.RequestSwitchFunction_data)
        assert type(msg) == RequestSwitchFunction
        assert msg.engage == True
        assert msg.thrown == False

    def test_RequestSwitchFunction_from_init(self):
        msg = RequestSwitchFunction(3, thrown=True, engage=True)
        assert msg.data == TestMessage.RequestSwitchFunction_data

    SwitchState_data = bytes([0xB1, 0x03, 0x30, 0x7D])

    def test_SwitchState_from_data(self):
        msg = SwitchState(TestMessage.SwitchState_data)
        assert type(msg) == SwitchState
        assert msg.address == 3
        assert msg.thrown == True
        assert msg.engage == True

    RequestSwitchState_data = bytes([0xBC, 0x03, 0x00, 0x40])

    def test_RequestSwitchState_from_data(self):
        msg = Message.from_data(TestMessage.RequestSwitchState_data)
        assert type(msg) == RequestSwitchState
        assert msg.address == 3

    def test_RequestSwitchState_from_init(self):
        msg = Message.from_data(TestMessage.RequestSwitchState_data)
        assert type(msg) == RequestSwitchState
        assert msg.address == 3

    SensorState_data = bytes([0xB2, 0x03, 0x30, 0x7E])

    def test_SensorState_from_data(self):
        msg = Message.from_data(TestMessage.SensorState_data)
        assert type(msg) == SensorState
        assert msg.address == 7
        assert msg.level == True

    LongAcknowledge_data = bytes([0xB4, 0x51, 0x01, 0x1B])

    def test_LongAcknowledge_from_data(self):
        msg = Message.from_data(TestMessage.LongAcknowledge_data)
        assert type(msg) == LongAcknowledge
        assert msg.ack1 == 1

    RequestSlotData_data = bytes([0xBB, 0x03, 0x00, 0x47])

    def test_RequestSlotData_from_init(self):
        msg = RequestSlotData(3)
        assert msg.data == TestMessage.RequestSlotData_data

    def test_RequestSlotData_from_data(self):
        msg = Message.from_data(TestMessage.RequestSlotData_data)
        assert type(msg) == RequestSlotData
        assert msg.slot == 3

    SlotDataReturn_data = bytes(
        [
            0xE7,
            0x0E,
            0x03,
            0x01,
            0x10,
            0x0B,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x0F,
        ]
    )

    def test_SlotDataReturn_from_data(self):
        msg = Message.from_data(TestMessage.SlotDataReturn_data)
        assert type(msg) == SlotDataReturn
        assert msg.slot == 3
        assert msg.address == 16
        assert msg.status == 1
        assert msg.speed == 11  # == 0.5 * (28 - 2) - 2
        assert msg.dir == False
        assert msg.f0 == False
        assert msg.f1 == False
        assert msg.f2 == False
        assert msg.f3 == False
        assert msg.f4 == False
        assert msg.f5 == False
        assert msg.f6 == False
        assert msg.f7 == False
        assert msg.f8 == False

    WriteSlotData_data = bytes(
        [
            0xEF,
            0x0E,
            0x03,
            0x01,
            0x10,
            0x0F,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x03,
        ]
    )

    def test_WriteSlotData_from_data(self):
        msg = Message.from_data(TestMessage.WriteSlotData_data)
        assert type(msg) == WriteSlotData
        assert msg.slot == 3
        assert msg.address == 16
        assert msg.status == 1
        assert msg.speed == 15
        assert msg.dir == False
        assert msg.f0 == False
        assert msg.f1 == False
        assert msg.f2 == False
        assert msg.f3 == False
        assert msg.f4 == False
        assert msg.f5 == False
        assert msg.f6 == False
        assert msg.f7 == False
        assert msg.f8 == False

    def test_WriteSlotData_from_init(self):
        slot = Slot(3, speed=0.5, status=1, address=16)
        msg = WriteSlotData(slot)
        assert msg.data == TestMessage.WriteSlotData_data

    SlotSpeed_data = bytes([0xA0, 0x03, 0x30, 0x6C])

    def test_SlotSpeed_from_data(self):
        msg = Message.from_data(TestMessage.SlotSpeed_data)
        assert type(msg) == SlotSpeed
        assert msg.slot == 3
        assert msg.speed == 48

    def test_SlotSpeed_from_init(self):
        msg = SlotSpeed(slot=3, speed=48)
        assert msg.data == TestMessage.SlotSpeed_data

    RequestLocAddress_data = bytes([0xBF, 0x03, 0x00, 0x43])

    def test_RequestLocAddress_from_data(self):
        msg = Message.from_data(TestMessage.RequestLocAddress_data)
        assert type(msg) == RequestLocAddress
        assert msg.address == 3

    def test_RequestLocAddress_from_init(self):
        msg = RequestLocAddress(3)
        assert msg.data == TestMessage.RequestLocAddress_data

    MoveSlots_data = bytes([0xBA, 0x03, 0x04, 0x42])

    def test_MoveSlots_from_data(self):
        msg = Message.from_data(TestMessage.MoveSlots_data)
        assert type(msg) == MoveSlots
        assert msg.src == 3
        assert msg.dst == 4

    def test_MoveSlots_from_init(self):
        msg = MoveSlots(src=3, dst=4)
        assert msg.data == TestMessage.MoveSlots_data

    CaptureTimeStamp_data = bytes([0xC0, 0x01, 0x02, 0x03, 0x04, 0x3B])

    def test_CaptureTimeStamp_from_data(self):
        msg = Message.from_data(TestMessage.CaptureTimeStamp_data)
        assert type(msg) == CaptureTimeStamp
        assert msg.time.hour == 1
        assert msg.time.minute == 2
        assert msg.time.second == 3
        assert msg.time.microsecond == 4 * 10000

    def test_CaptureTimeStamp_from_init(self):
        from datetime import time

        t = time(hour=1, minute=2, second=3, microsecond=40000)
        msg = CaptureTimeStamp(t)
        assert msg.data == TestMessage.CaptureTimeStamp_data

    def test_Unknown_from_data(self):
        assert type(Message.from_data(bytes([0xD0, 0, 0, 0, 0, 0x2F]))) == Unknown
