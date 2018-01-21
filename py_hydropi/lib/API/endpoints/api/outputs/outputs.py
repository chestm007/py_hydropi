from py_hydropi.lib.API.api_endpoint_base import APIEndpointBase


class Outputs(APIEndpointBase):
    def _get(self):
        return ['air_pumps', 'water_pumps', 'lights']
