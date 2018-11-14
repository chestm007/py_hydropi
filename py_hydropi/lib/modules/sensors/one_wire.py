from py_hydropi.lib.modules.inputs import Input


class OneWireInput(Input):
    provides = ('DS18B20', )
    _parsers = {'28-041752029bff': lambda i: int(i.splitlines()[1].split('t=')[1]) / 1000.0}
    _path = '/sys/bus/w1/devices'
    _sensor_template = '{path}/{sensor_id}/w1_slave'
    frequency = 10

    def __init__(self, sensor_id=None, **kwargs):
        super().__init__(**kwargs)
        assert sensor_id

        self.sensor_id = sensor_id
        self._sensor_path = self._sensor_template.format(path=self._path,
                                                         sensor_id=self.sensor_id)

    def _read(self):
        try:
            with open(self._sensor_path) as s:
                try:
                    return self._parsers[self.sensor_id](s.read())

                except KeyError:
                    self.logger.error('parser not defined for: {}'.format(self.sensor_id))

                except IndexError:
                    self.logger.error('error reading sensor data')
                    return

        except FileNotFoundError:
            self.logger.error('specified sensor not found: {}\nexiting monitoing thread'.format(self._sensor_path))
            self._continue = False
