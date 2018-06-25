from py_hydropi.lib.modules.inputs import Input


class MemDatabase(object):
    def __init__(self, queue):
        self.controllers = {}
        self.gpio = None
        self.server_queue = queue
        self._inputs = {}

    def get_input(self, input_id):
        if input_id not in self._inputs.keys():
            self._inputs[input_id] = Input(input_id).start()
        return self._inputs[input_id]

