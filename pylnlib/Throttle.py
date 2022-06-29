class Throttle:
    def __init__(self, scrollkeeper, locaddress):
        self.scrollkeeper = scrollkeeper
        self.locaddress = locaddress
        
    def forward(self):
        slot = self.scrollkeeper.getSlot(self.locoaddress)
        slot.dir = False
        self.scrollkeeper.sendMessage(slot.slotWriteMessage())
