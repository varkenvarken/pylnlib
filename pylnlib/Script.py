# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220705170908

from time import sleep, time

from .Message import RequestSwitchFunction
from .Scrollkeeper import Scrollkeeper
from .Throttle import Throttle


class Script:
    def __init__(self, scrollkeeper: Scrollkeeper):
        self.scrollkeeper = scrollkeeper

    def wait(self, seconds):
        sleep(seconds)

    def waitForSensor(self, id, state, timeout=60):
        start = time()
        while time() - start < timeout:
            sensorstate = self.scrollkeeper.getSensorState(id)
            if sensorstate == state:
                return True
            sleep(0.1)
        return False

    # waitForSwitch(switchaddress, state, timeout=60)

    def setSwitch(self, address, thrown):
        msg1 = RequestSwitchFunction(address, thrown, True)
        msg2 = RequestSwitchFunction(address, thrown, False)
        self.scrollkeeper.sendMessage(msg1)
        sleep(1.5)
        self.scrollkeeper.sendMessage(msg2)

    def getThrottle(self, locaddress):
        return self.scrollkeeper.getThrottle(locaddress)

    # powerOff
    # powerOn
