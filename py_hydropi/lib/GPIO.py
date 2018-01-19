import RPi.GPIO


class GPIO(object):
    def __init__(self):
        self.GPIO = RPi.GPIO
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
