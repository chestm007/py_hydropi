from datetime import datetime, timedelta, time
from time import sleep

from py_hydropi.lib import Output
from py_hydropi.lib.modules.switch import Switch
from ..time_utils import parse_clock_time_string, parse_simple_time_string, time_to_datetime


class Timer(Switch):
    def __init__(self):
        super().__init__()
        self.attached_triggered_outputs = {}
        self.activated_time = None  # type: datetime
        self.deactivated_time = None  # type: datetime
        self.triggered_outputs_activated = False

    @property
    def all_outputs(self):
        out = super().all_outputs
        for outputs in self.attached_triggered_outputs.values():
            out.extend(outputs.get('objects'))
        return out

    def _activate_objects(self, activated_time=None):
        if not self.outputs_activated:
            self.activated_time = activated_time or datetime.now()
            self.deactivated_time = None
            super()._activate_objects()

    def _deactivate_objects(self, deactivaed_time=None):
        if self.outputs_activated:
            self.activated_time = None
            self.deactivated_time = deactivaed_time or datetime.now()
            super()._deactivate_objects()

    def _activate_triggered_objects(self, group_name):
        if not self.triggered_outputs_activated:
            for output in self.attached_triggered_outputs[group_name]['objects']:
                if output.manual_control:
                    self.logger.info('output {} is manually controlled, skipping signal'.format(output.channel))
                else:
                    self.logger.info('signalling triggered output {} to activate'.format(output.channel))
                    output.activate()
                self.triggered_outputs_activated = True

    def _deactivate_triggered_objects(self, group_name):
        if self.triggered_outputs_activated:
            for output in self.attached_triggered_outputs[group_name]['objects']:
                if output.manual_control:
                    self.logger.info('output {} is manually controlled, skipping signal'.format(output.channel))
                else:
                    self.logger.info('signalling triggered output {} to deactivate'.format(output.channel))
                    output.deactivate()
                self.triggered_outputs_activated = False

    def attach_triggered_object(self, obj, group_name, before, after):
        if group_name not in self.attached_triggered_outputs.keys():
            self.attached_triggered_outputs[group_name] = {
                'objects': [],
                'before': parse_simple_time_string(before),
                'after': parse_simple_time_string(after)
            }

        if type(obj) in (list, tuple):
            self.attached_triggered_outputs[group_name]['objects'].extend(obj)
        else:
            self.attached_triggered_outputs[group_name]['objects'].append(obj)

        return self

    def _check_timer(self):
        """
        extend this function in inherited timer classes to check
        timer conditions and sets output status accordingly
        :return: nothing
        """
        raise NotImplementedError()

    def _check_before_trigger(self):
        raise NotImplementedError()

    def _check_after_trigger(self):
        raise NotImplementedError()

    def _main_loop(self):
        while self._continue:
            self._check_timer()
            self._check_after_trigger()
            self._check_before_trigger()
            sleep(0.1)

    def stop(self):
        for group in self.attached_triggered_outputs.keys():
            self._deactivate_triggered_objects(group)
        super(Timer, self).stop()

    def to_json(self):
        return {
            'attached_outputs': [o.to_json() for o in self.attached_outputs],
            'attached_triggered_outputs': self._decode_attached_triggered_outputs(),
            'active': self._continue,
            'outputs_activated': self.outputs_activated,
            'triggered_outputs_activated': self.triggered_outputs_activated
        }

    def _decode_attached_triggered_outputs(self):
        out_dict = {}
        for group_name, param_dict in self.attached_triggered_outputs.items():
            out_dict[group_name] = {'before': param_dict.get('before'),
                                    'after': param_dict.get('after'),
                                    'objects': [o.to_json() for o in param_dict.get('objects')]
                                    }
        return out_dict

    @classmethod
    def load_config(cls, raspberry_pi_timer, config):
        raise NotImplementedError


class ClockTimer(Timer):
    def __init__(self, active_hours):
        self.on_time, self.off_time = parse_clock_time_string(active_hours)
        super().__init__()

    @staticmethod
    def _get_current_time():
        return datetime.now()

    @staticmethod
    def time_in_range(start, end, x):
        """Return true if x is in the range [start, end]"""
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end

    def _check_timer(self):
        now = self._get_current_time().time()
        on = time_to_datetime(now, self.on_time).time()
        off = time_to_datetime(now, self.off_time).time()
        if self.outputs_activated:
            if self.time_in_range(off, on, now):
                self._deactivate_objects(now)
        else:
            if self.time_in_range(on, off, now):
                self._activate_objects(now)

    def _check_before_trigger(self):
        for group_name, opts in self.attached_triggered_outputs.items():
            now = datetime.now()
            on_string = now.strftime('%b %d %Y {}'.format(self.on_time))
            on_datetime = datetime.strptime(on_string, '%b %d %Y %I:%M%p')
            if on_datetime < now:
                on_datetime += timedelta(days=1)
            if on_datetime - timedelta(seconds=opts['before']) > now:
                self._activate_triggered_objects(group_name)

    def _check_after_trigger(self):
        for group_name, opts in self.attached_triggered_outputs.items():
            now = datetime.now()
            off_string = now.strftime('%b %d %Y {}'.format(self.off_time))
            off_datetime = datetime.strptime(off_string, '%b %d %Y %I:%M%p')
            if off_datetime < now:
                off_datetime += timedelta(days=1)
            if off_datetime + timedelta(seconds=opts['after']) > now:
                self._deactivate_triggered_objects(group_name)

    @classmethod
    def load_config(cls, raspberry_pi_timer, config):
        return {group: cls(
            active_hours=group_settings.get('active_hours')
        ).attach_object(
            [Output(raspberry_pi_timer, chan)
             for chan in group_settings.get('channels')]
        ) for group, group_settings in config.items()}


class SimpleTimer(Timer):
    def __init__(self, on_time, off_time):
        self.on_time = parse_simple_time_string(on_time)  # type: int
        self.off_time = parse_simple_time_string(off_time)  # type: int
        super().__init__()

    @classmethod
    def load_config(cls, raspberry_pi_timer, config):
        return {group: cls(
            on_time=group_settings.get('on_time'),
            off_time=group_settings.get('off_time')
        ).attach_object(
            [Output(raspberry_pi_timer, chan)
             for chan in group_settings.get('channels')]
        ) for group, group_settings in config.items()}

    def _check_timer(self):
        now = datetime.now()
        if not self.outputs_activated:
            if self.deactivated_time is None or self.deactivated_time + timedelta(seconds=self.off_time) < now:
                self.activated_time = datetime.now()
                self._activate_objects()

        else:
            if self.activated_time is None or self.activated_time + timedelta(seconds=self.on_time) < now:
                self.deactivated_time = datetime.now()
                self._deactivate_objects()

    def _check_before_trigger(self):
        for group_name, opts in self.attached_triggered_outputs.items():
            if not self.triggered_outputs_activated:
                if self.deactivated_time:
                    now = datetime.now()
                    if self.deactivated_time + timedelta(seconds=self.off_time) - timedelta(seconds=opts['before']) < now:
                        self._activate_triggered_objects(group_name)

    def _check_after_trigger(self):
        for group_name, opts in self.attached_triggered_outputs.items():
            if self.triggered_outputs_activated:
                if self.activated_time:
                    now = datetime.now()
                    if self.activated_time + timedelta(seconds=self.on_time) + timedelta(seconds=opts['after']) < now:
                        self._deactivate_triggered_objects(group_name)
