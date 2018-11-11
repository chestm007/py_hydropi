from py_hydropi.lib.iter_utils import JSONableDict, JSONableList


class MemDatabase(object):
    def __init__(self, queue):
        self.controllers = JSONableDict()
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

    def outputs(self):
        outputs = JSONableList()
        for type_, value in self.controllers.items():
            for name_, switch in value.items():
                if hasattr(switch, 'all_outputs'):
                    outputs.extend_if_not_in(switch.all_outputs)
        return outputs

    @property
    def inputs(self):
        return self._inputs
