import threading


class Script:
    def __init__(self, scriptrunner, stream):
        self.scriptrunner = scriptrunner
        self.stream = stream
        self.locals = {
            "log": self.scriptrunner.log,
            "wait": self.scriptrunner.wait,
            "waitForSensor": self.scriptrunner.waitForSensor,
            "setSwitch": self.scriptrunner.setSwitch,
            "getThrottle": self.scriptrunner.getThrottle,
        }

    def execute(self):
        exec(self.stream, None, self.locals)

    def run(self):
        threading.Thread(name="script", target=self.execute, daemon=True).start()
