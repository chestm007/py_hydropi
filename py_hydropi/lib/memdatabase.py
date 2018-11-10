class MemDatabase(object):
    def __init__(self, queue):
        self.controllers = {}
        self.gpio = None
        self.server_queue = queue
        self._inputs = {}

    def get_input(self, sensor_id=None):
        return self._inputs.get(sensor_id)

    def get_output(self, output_id):
        type_, name_ = output_id.split('.')
        group = self.controllers.get(type_)
        if group:
            return group.get(name_)

    @property
    def inputs(self):
        return self._inputs
