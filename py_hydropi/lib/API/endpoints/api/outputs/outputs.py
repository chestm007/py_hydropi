from py_hydropi.lib.API.api_endpoint_base import APIEndpointBase


class Outputs(APIEndpointBase):
    def _get(self):
        return self.api.db.controllers

    @staticmethod
    def _put_(data, output_type):
        group = data.get('group')
        channel = data.get('channel')
        state = data.get('state')
        manual_control = data.get('manual_control')
        if not ((group or channel) and (state or manual_control)):
            return 'missing required parameters [group|channel] [state|manual_control]'
        output_type_group = output_type.get(group)
        for output_type in output_type_group:
            if channel is not None:
                if output_type.channel != channel:
                    continue
            if state is not None:
                output_type.set_state(state)
            if manual_control is not None:
                output_type.manual_control = manual_control
        return True
