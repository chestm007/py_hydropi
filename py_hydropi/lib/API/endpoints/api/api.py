from py_hydropi.lib.API.api_endpoint_base import APIEndpointBase


class Api(APIEndpointBase):
    def _get(self):
        return ['outputs', 'timers']
