from pylnlib.Message import (
    PowerOn,
    PowerOff,
    Message,
    FunctionGroup1,
    FunctionGroupSound,
)


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
