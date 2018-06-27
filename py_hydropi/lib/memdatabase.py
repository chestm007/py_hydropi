from py_hydropi.lib.modules.inputs import Input


class MemDatabase(object):
    def __init__(self, queue):
        self.controllers = {}
        self.gpio = None
        self.server_queue = queue
        self._inputs = {}

    def get_input(self, sensor_id=None, sensor_channel=None):
        if sensor_id not in self._inputs.keys():
            self._inputs[sensor_id] = Input(sensor_id=sensor_id).start()
        return self._inputs[sensor_id]

