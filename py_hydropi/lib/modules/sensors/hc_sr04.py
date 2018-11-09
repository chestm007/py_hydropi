from hcsr04sensor import sensor

from py_hydropi.lib.modules.inputs import Input


class UltrasonicInput(Input):
    provides = ('HC_SR04', 'HCSR04')
    frequency = 30

    def __init__(self, channels=None, pi_timer=None, correction=None, **kwargs):
        super().__init__(**kwargs)
        assert channels and pi_timer

        self.gpio = pi_timer.gpio
        self.echo = channels.get('out')
        self.trigger = channels.get('in')
        self.channels = channels
        if correction is not None:
            self.correction = pi_timer.db.get_input(correction)  # type: Input
        else:
            self.correction = None  # type: Input

    def _read(self):
        value = sensor.Measurement(self.trigger,
                                   self.echo,
                                   temperature=self.correction.value)
        try:
            distance = value.raw_distance(sample_size=11, sample_wait=0.2)
            return round(distance, 2)
        except SystemError:
            self.logger.error('echo pulse not recieved {}'.format(self.channels))

