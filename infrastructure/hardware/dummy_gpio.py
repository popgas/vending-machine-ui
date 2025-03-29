class DummyGPIO:
    BOARD = 'BOARD'
    BCM = 'BCM'
    IN = 'IN'
    OUT = 'OUT'
    LOW = False
    HIGH = True
    PUD_UP = 'PUD_UP'
    PUD_DOWN = 'PUD_DOWN'
    PUD_OFF = 'PUD_OFF'

    def setup(self, v1, v2, pull_up_down=None):
        pass
    def cleanup(self):
        pass
    def configure(self, pin):
        pass
    def output(self, pin, v1):
        pass
    def set_mode(self, mode):
        pass
    def setwarnings(self, flag):
        pass
    def setmode(self, flag):
        pass