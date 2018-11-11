from py_hydropi.lib.API.api_endpoint_base import APIEndpointBase


class Outputs(APIEndpointBase):
    def _get(self):
        out = self.api.db.outputs().to_json()
        return out
