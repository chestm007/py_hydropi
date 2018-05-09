from py_hydropi.lib.API.endpoints.api.outputs.outputs import Outputs


class Lights(Outputs):
    def _get(self):
        return {k: [e.to_json() for e in v] for k, v in self.api.db.lights.items()}

    def _put(self, data):
        return super()._put_(data, self.api.db.lights)
