import os

from .logger import Logger

if os.environ.get('PY_HYDROPI_TESTING', '').lower() == 'true':
    # noinspection PyUnusedLocal
    class RPIGPIO:
        class Bcm:
            pass

        class In:
            pass

        class Out:
            pass

        class High:
            pass

        class Low:
            pass

        BCM = Bcm()
        IN = In()
        OUT = Out()
        HIGH = High()  # OFF
        LOW = Low()    # ON

        @staticmethod
        def setmode(mode):
            assert isinstance(mode, RPIGPIO.Bcm)

        @staticmethod
        def cleanup():
            return

        @staticmethod
        def setup(channel, input_output, pull_up_down=None, initial=None):
            assert type(channel) == int
            assert isinstance(input_output, (RPIGPIO.In, RPIGPIO.Out, RPIGPIO.High, RPIGPIO.Low))

        @staticmethod
        def output(channel, state):
            assert type(channel) == int
            assert isinstance(state, (RPIGPIO.High, RPIGPIO.Low))

        @staticmethod
        def input(channel):
            assert type(channel) == int
else:
    import RPi.GPIO as RPIGPIO


# noinspection PyUnusedLocal
class GPIO(object):
    def __init__(self):
        self._GPIO = RPIGPIO  # type: RPIGPIO
        self._GPIO.setmode(self._GPIO.BCM)
        self.logger = Logger('GPIO')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._GPIO.cleanup()

    def setup_input_channel(self, channel: int, pull_up_down=None):
        self._GPIO.setup(int(channel), self._GPIO.IN)

    def setup_output_channel(self, channel: int, initial_state=False):
        try:
            self._GPIO.setup(int(channel), self._GPIO.OUT)
            self.logger.debug('set channel {} as output'.format(channel))
        except ValueError:
            self.logger.error('error processing channel {}'.format(channel))

    def set_output_on(self, channel):
        try:
            self._GPIO.output(channel, self._GPIO.LOW)
        except RuntimeError:
            self.logger.error('error setting channel {} on'.format(channel))

    def set_output_off(self, channel):
        try:
            self._GPIO.output(channel, self._GPIO.HIGH)
        except RuntimeError:
            self.logger.error('error setting channel {} off'.format(channel))

    def get_input(self, channel):
        return self._GPIO.input(channel)

    def cleanup(self):
        self._GPIO.cleanup()
