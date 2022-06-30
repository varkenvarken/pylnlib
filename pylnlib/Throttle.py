# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220629204333
class Throttle:
    """
    A class to control a single locomotive.
    """
    def __init__(self, scrollkeeper, locaddress):
        self.scrollkeeper = scrollkeeper
        self.locaddress = locaddress
        
    def forward(self):
        slot = self.scrollkeeper.getSlot(self.locoaddress)
        slot.dir = False
        self.scrollkeeper.sendMessage(slot.slotWriteMessage())

    def reverse(self):
        slot = self.scrollkeeper.getSlot(self.locoaddress)
        slot.dir = True
        self.scrollkeeper.sendMessage(slot.slotWriteMessage())
