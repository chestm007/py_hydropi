import os

if os.environ.get('PY_HYDROPI_TESTING', '').lower() != 'true':
    from hcsr04sensor import sensor
else:
    class Sensor:
        class Measurement:
            def __init__(self, trig, echo, temperature=20, sample_size=1):
                assert type(trig) == int
                assert type(echo) == int
                assert type(temperature) in (float, int)
                assert type(sample_size) == int

                self.trig = trig
                self.echo = echo
                self.temperature = temperature
                self.sample_size = sample_size
                self._value = 50

            def raw_distance(self, sample_size=1, **_):
                assert type(sample_size) == int
                return self._value
    sensor = Sensor()

from py_hydropi.lib.modules.inputs import Input


class UltrasonicInput(Input):
    provides = ('HC_SR04', 'HCSR04')
    frequency = 30

    def __init__(self, channels=None, pi_timer=None, correction=None, **kwargs):
        super().__init__(**kwargs)
        assert channels and pi_timer

        self.pi_timer = pi_timer
        self.echo = channels.get('echo')
        self.trigger = channels.get('trigger')
        self.channels = channels
        self._correction_identifier = correction
        if correction is not None:
            self.correction = self._get_correction_input()  # type: Input
        else:
            self.correction = None  # type: Input

    def _get_correction_input(self):
        return self.pi_timer.db.get_input(self._correction_identifier)  # type: Input

    def _read(self):
        if self.correction is None:
            correction = self._get_correction_input()
            if isinstance(correction, Input):
                self.correction = correction

        try:
            value = sensor.Measurement(
                self.trigger,
                self.echo,
                temperature=(
                    self.correction.value
                    if self.correction is not None
                    and self.correction.value is not None
                    else 20))
            distance = value.raw_distance(sample_size=11, sample_wait=0.2)
            return round(distance, 2)
        except Exception as e:
            self.logger.error('{} channels:{}'.format(e, self.channels))
