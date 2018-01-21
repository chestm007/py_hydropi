from py_hydropi.lib.API.api_endpoint_base import APIEndpointBase


class Timers(APIEndpointBase):
    def _get(self):
        return {k: v.toJSON() for k, v in self.api.db.timers.items()}
