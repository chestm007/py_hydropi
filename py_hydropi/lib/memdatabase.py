from py_hydropi.lib.modules.inputs import Input


class MemDatabase(object):
    def __init__(self, queue):
        self.controllers = {}
        self.gpio = None
        self.server_queue = queue
        self._inputs = {}

    def get_input(self, sensor_id=None):
        if sensor_id not in self._inputs.keys():
            print(sensor_id)
            self._inputs[sensor_id] = Input(sensor_id=sensor_id).start()
        return self._inputs[sensor_id]

    def get_output(self, output_id):
        type_, name_ = output_id.split('.')
        group = self.controllers.get(type_)
        if group:
            return group.get(name_)