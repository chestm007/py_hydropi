from py_hydropi.lib.API.api_endpoint_base import APIEndpointBase


class Controllers(APIEndpointBase):
    def _get(self):
        return self.api.db.controllers.to_json()
