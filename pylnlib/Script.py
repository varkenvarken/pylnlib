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
     # waitForSwitch(switchaddress, state, timeout=60)
     # setSwitch(switchaddress, state, timeout=60)
     # acquireLocomotive(locaddress, timeout=60)
     # setSpeed(locaddress, direction, speed:float, timeout=60)
     # setFunction(locaddress, function, state, duration=0, timeout=60)
     # powerOff
     # powerOn
     # aliases:
     # lightOn
     # soundOn
     # whistle
        
