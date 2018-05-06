import os

from .logger import Logger

if os.environ.get('PY_HYDROPI_TESTING') != 'true':
    import RPi.GPIO as RPIGPIO
else:
    class RPIGPIO(object):
        class Bcm(object):
            pass

        class In(object):
            pass

        class Out(object):
            pass
        BCM = Bcm()
        IN = In()
        OUT = Out()

        @staticmethod
        def setmode(mode):
            assert isinstance(mode, RPIGPIO.Bcm)

        @staticmethod
        def cleanup():
            return

        @staticmethod
        def setup(channel, input_output, pull_up_down=None, initial=None):
            assert type(channel) == int
            assert (isinstance(input_output, RPIGPIO.In) or isinstance(input_output, RPIGPIO.Out))
            #assert pull_up_down is not None or initial is not None

        @staticmethod
        def output(channel, state):
            assert type(channel) == int
            assert type(state) == bool

        @staticmethod
        def input(channel):
            assert type(channel) == int


class GPIO(object):
    def __init__(self):
        self.GPIO = RPIGPIO  # type: RPIGPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.logger = Logger('GPIO')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.GPIO.cleanup()

    def setup_input_channel(self, channel: int, pull_up_down=None):
        self.GPIO.setup(int(channel), self.GPIO.IN, pull_up_down=pull_up_down or self.GPIO.PUD_DOWN)

    def setup_output_channel(self, channel: int, initial_state=False):
        try:
            self.GPIO.setup(int(channel), self.GPIO.IN)
        except ValueError:
            self.logger.error('error processing channel {}'.format(channel))

    def set_output_on(self, channel):
        self.GPIO.setup(channel, self.GPIO.OUT)

    def set_output_off(self, channel):
        self.GPIO.setup(channel, self.GPIO.IN)

    def get_input(self, channel):
        return self.GPIO.input(channel)


