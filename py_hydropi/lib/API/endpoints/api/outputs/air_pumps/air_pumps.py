from py_hydropi.lib.API.endpoints.api.outputs.outputs import Outputs


class AirPumps(Outputs):
    def _get(self):
        return {k: [e.to_json() for e in v] for k, v in self.api.db.air_pumps.items()}

    def _put(self, data):
        return super()._put_(data, self.api.db.air_pumps)
