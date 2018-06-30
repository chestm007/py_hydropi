import time

from py_hydropi.lib.modules.inputs import Input


class UltrasonicInput(Input):
    provides = ('HC_SR04')
    SPEED_OF_SOUND = 343
    FACTOR = 50

    def __init__(self, channels=None, pi_timer=None, correction=None, **kwargs):
        super().__init__(**kwargs)
        assert channels and pi_timer

        self.gpio = pi_timer.gpio
        self.gpio.set_output_on(channels.get('out'))
        self.gpio.setup_input_channel(channels.get('in'))
        self.gpio._GPIO.output(channels.get('out'), False)
        self.channels = channels
        if correction is not None:
            self.correction = pi_timer.db.get_input(correction)
        else:
            self.correction = None

    @property
    def speed_of_sound(self):
        if self.correction:
            return self.SPEED_OF_SOUND + (0.6 * (self.correction.value - 20))
        else:
            return self.SPEED_OF_SOUND

    def _read(self):
        self.gpio._GPIO.output(self.channels.get('out'), True)
        time.sleep(0.00001)
        self.gpio._GPIO.output(self.channels.get('out'), False)

        pulse_end, pulse_start = [None]*2

        while self.gpio._GPIO.input(self.channels.get('in')) == 0:
            pulse_start = time.time()

        while self.gpio._GPIO.input(self.channels.get('in')) == 1:
            pulse_end = time.time()
        if pulse_start is not None and pulse_end is not None:
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * (self.speed_of_sound * self.FACTOR)

            return round(distance, 2)
