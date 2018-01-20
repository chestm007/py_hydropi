import os
if os.environ['PY_HYDROPI_TESTING'] != 'true':
    import RPi.GPIO as RPiGPIO
else:

    class RPiGPIO(object):
        class Board(object):
            pass

        class In(object):
            pass

        class Out(object):
            pass
        BOARD = Board()
        IN = In()
        OUT = Out()

        @staticmethod
        def setmode(mode):
            print(type(mode))
            assert isinstance(mode, RPiGPIO.Board)

        @staticmethod
        def cleanup():
            return

        @staticmethod
        def setup(channel, input_output, pull_up_down=None, initial=None):
            assert type(channel) == int
            assert (isinstance(input_output, RPiGPIO.In) or isinstance(input_output, RPiGPIO.Out))
            assert pull_up_down is not None or initial is not None

        @staticmethod
        def output(channel, state):
            assert type(channel) == int
            assert type(state) == bool

        @staticmethod
        def input(channel):
            assert type(channel) == int

            #RPi.GPIO.input = input
            #RPi.GPIO.output = output
            #RPi.GPIO.setup = setup
            #RPi.GPIO.cleanup = cleanup
            #RPi.GPIO.setmode = setmode


class GPIO(object):
    def __init__(self):
        self.GPIO = RPiGPIO
        self.GPIO.setmode(self.GPIO.BOARD)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.GPIO.cleanup()

    def setup_input_channel(self, channel: int, pull_up_down=None):
        self.GPIO.setup(int(channel), self.GPIO.IN, pull_up_down=pull_up_down or self.GPIO.PUD_DOWN)

    def setup_output_channel(self, channel: int, initial_state=False):
        try:
            self.GPIO.setup(int(channel), self.GPIO.OUT, initial=initial_state)
        except Exception:
            print('error processing channel {}'.format(channel))

    def set_output_on(self, channel):
        self.GPIO.output(channel, True)

    def set_output_off(self, channel):
        self.GPIO.output(channel, False)

    def get_input(self, channel):
        return self.GPIO.input(channel)


