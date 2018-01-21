from py_hydropi.lib.API.api_endpoint_base import APIEndpointBase


class AirPumps(APIEndpointBase):
    def _get(self):
        return {k: [e.toJSON() for e in v] for k, v in self.api.db.air_pumps.items()}
