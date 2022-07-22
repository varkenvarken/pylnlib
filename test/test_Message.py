from pylnlib.Message import PowerOn, Message


class TestMessage:
    def test_PowerOn(self):
        assert type(Message.from_data(bytes([0x83, 0x7C]))) == PowerOn
