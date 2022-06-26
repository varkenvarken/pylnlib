# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220625153535

from time import sleep, time

from .Scrollkeeper import Scrollkeeper

class Script:
    def __init__(self, scrollkeeper:Scrollkeeper):
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
