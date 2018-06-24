from py_hydropi.lib import Output, parse_simple_time_string, parse_clock_time_string
from py_hydropi.lib.API.api_endpoint_base import APIEndpointBase


class Timers(APIEndpointBase):
    def _get(self):
        return {k: v.to_json() for k, v in self.api.db.timers.items()}

    def _post(self, data):
        pass

    def _put(self, data):
        """
        JSON document of all possible args
        {
            "group": "water_pumps.group1",
            "on_time": "5m",
            "off_time": "5m",
            "active_hours": "4:00am - 10:00pm",
            "timer_active": True,
            "attach_output": {
                "channel": 10,
                "type": "water_pumps"
            },
            "attach_triggered_output": {
                "output": {
                    "channel": 11,
                    "type": "air_pumps"
                },
                "before": "1m",
                "after": "1m",
                "group_name": "group1
            }
        }
        :param data: the above JSON, or a subset of it
        """
        group = data.get('group')
        timer = self.api.db.timers.get(group)
        if not timer:
            return 'timer not found matching group {}'.format(group)

        on_time = data.get('on_time')
        off_time = data.get('off_time')
        active_hours = data.get('active_hours')
        if any([on_time, off_time, active_hours]):
            if (on_time or off_time) or active_hours:
                return 'can only specify on_time and off_time or active hours'
        if on_time:
            timer.on_time = parse_simple_time_string(on_time)
        if off_time:
            timer.off_time = parse_simple_time_string(off_time)
        if active_hours:
            timer.on_time, timer.off_time = parse_clock_time_string(active_hours)

        timer_active = data.get('timer_active')
        if timer_active is not None:
            if type(timer_active) != bool:
                return 'timer_active bust be a boolean value'
            timer._continue = timer_active
            if timer_active:
                timer.start()

        attach_output = data.get('attach_output')
        if attach_output:
            output_channel = attach_output.get('channel')
            if not output_channel:
                return 'you must specify channel for attach_output'
            output_type = attach_output.get('type')
            if output_type not in Output.types:
                return 'you must specify type for attach_output [lights|water_pumps|air_pumps]'
            else:
                output_object = Output(
                    gpio=self.api.db.gpio,
                    channel=output_channel,
                    output_type=output_type)
                timer.attach_object(output_object)
            if getattr(self.api.db, output_type).get(group) is not None:
                getattr(self.api.db, output_type).get(group).append(output_object)
            else:
                getattr(self.api.db, output_type)[group] = [output_object]
            if group not in self.api.db.groups:
                self.api.db.groups.append(group)

        attach_triggered_output = data.get('attach_triggered_output')
        if attach_triggered_output:
            triggered_output = attach_triggered_output.get('output')
            if triggered_output:
                triggered_output_channel = triggered_output.get('channel')
                if not triggered_output_channel:
                    return 'you must specify channel for output'
                triggered_output_type = triggered_output.get('type')
                if not triggered_output_type:
                    return 'you must specify type for output'
            else:
                return 'you must specify output for attach_triggered_output'
            triggered_group_name = attach_triggered_output.get('group_name')
            if not triggered_group_name:
                return 'you must specify group_name for attach_triggered_output'
            triggered_before = attach_triggered_output.get('before')
            if not triggered_before:
                return 'you must specify before for attach_triggered_output'
            triggered_after = attach_triggered_output.get('after')
            if not triggered_after:
                return 'you must specify after for attach_triggered_output'
            triggered_output_object = Output(
                gpio=self.api.db.gpio,
                channel=triggered_output_channel,
                output_type=triggered_output_type),
            timer.attach_triggered_object(
                obj=triggered_output_object,
                group_name=triggered_output_type + '.' + triggered_group_name,
                before=triggered_before,
                after=triggered_after)
            getattr(self.api.db, triggered_output_type).get(group)
            if getattr(self.api.db, triggered_output_type).get(group) is not None:
                getattr(self.api.db, triggered_output_type).get(group).append(triggered_output_object)
            else:
                getattr(self.api.db, triggered_output_type)[group] = [triggered_output_object]
            if triggered_group_name not in self.api.db.groups:
                self.api.db.groups.append(triggered_group_name)

        return True

