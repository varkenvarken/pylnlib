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
        
    def forward(self, speed=0):
        slot = self.scrollkeeper.getSlot(self.locoaddress)
        slot.dir = False
        slot.setSpeed(speed)
        self.scrollkeeper.sendMessage(slot.slotWriteMessage())

    def reverse(self, speed=0):
        slot = self.scrollkeeper.getSlot(self.locoaddress)
        slot.dir = True
        slot.setSpeed(speed)
        self.scrollkeeper.sendMessage(slot.slotWriteMessage())
        
    def lights(self, on=True, duration=0):
        slot = self.scrollkeeper.getSlot(self.locoaddress)
        slot.function(0, on, duration)
        
     def whistle(self, on=True, duration=0.5):
        slot = self.scrollkeeper.getSlot(self.locoaddress)
        slot.function(1, on, duration)
 
