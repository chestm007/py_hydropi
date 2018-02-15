from datetime import datetime, timedelta
from threading import Thread
from time import sleep
from ..logger import Logger
from ..time_utils import parse_clock_time_string, parse_simple_time_string


def timer_factory(timer_type, **params):
    if timer_type == 'clock':
        return ClockTimer(**params)
    if timer_type == 'simple':
        return SimpleTimer(**params)


class Timer(object):
    logger = Logger('Timer')

    def __init__(self):
        self.attached_outputs = []
        self.attached_triggered_outputs = {}
        self.activated_time = None  # type: datetime
        self.deactivated_time = datetime.now()  # type: datetime
        self._continue = True  # set to false to exit self._timer_loop
        self.outputs_activated = False
        self.triggered_outputs_activated = False
        self.timer_thread = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def attach_object(self, obj):
        self.attached_outputs.append(obj)

    def _activate_objects(self):
        if not self.outputs_activated:
            for output in self.attached_outputs:
                if output.manual_control:
                    self.logger.info('output {} is manually controlled, skipping signal'.format(output.channel))
                else:
                    self.logger.info('signalling output {} to activate'.format(output.channel))
                    output.activate()
            self.outputs_activated = True

    def _deactivate_objects(self):
        if self.outputs_activated:
            for output in self.attached_outputs:
                if output.manual_control:
                    self.logger.info('output {} is manually controlled, skipping signal'.format(output.channel))
                else:
                    self.logger.info('signalling output {} to deactivate'.format(output.channel))
                    output.deactivate()
            self.outputs_activated = False

    def _activate_triggered_objects(self, group_name):
        if not self.triggered_outputs_activated:
            for output in self.attached_triggered_outputs[group_name]['objects']:
                if output.manual_control:
                    self.logger.info('output {} is manually controlled, skipping signal'.format(output.channel))
                else:
                    self.logger.info('signalling output {} to activate'.format(output.channel))
                    output.activate()
                self.triggered_outputs_activated = True

    def _deactivate_triggered_objects(self, group_name):
        if self.triggered_outputs_activated:
            for output in self.attached_triggered_outputs[group_name]['objects']:
                if output.manual_control:
                    self.logger.info('output {} is manually controlled, skipping signal'.format(output.channel))
                else:
                    self.logger.info('signalling output {} to deactivate'.format(output.channel))
                    output.deactivate()
                self.triggered_outputs_activated = False

    def attach_triggered_object(self, obj, group_name, before, after):
        if group_name in self.attached_triggered_outputs.keys():
            self.attached_triggered_outputs[group_name]['objects'].append(obj)
        else:
            self.attached_triggered_outputs[group_name] = {
                'objects': [obj],
                'before': parse_simple_time_string(before),
                'after': parse_simple_time_string(after)
            }

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

    def start(self):
        self.timer_thread = Thread(target=self._timer_loop)
        self.timer_thread.start()

    def stop(self):
        self._deactivate_objects()
        for group in self.attached_triggered_outputs.keys():
            self._deactivate_triggered_objects(group)
        self._continue = False

    def _timer_loop(self):
        while self._continue:
            self._check_timer()
            self._check_after_trigger()
            self._check_before_trigger()
            sleep(0.5)
        self.stop()

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


class ClockTimer(Timer):
    def __init__(self, active_hours):
        self.on_time, self.off_time = parse_clock_time_string(active_hours)
        super().__init__()

    def _check_timer(self):
        now = datetime.now()
        on_string = now.strftime('%b %d %Y {}'.format(self.on_time))
        on_datetime = datetime.strptime(on_string, '%b %d %Y %I:%M%p')
        off_string = now.strftime('%b %d %Y {}'.format(self.off_time))
        off_datetime = datetime.strptime(off_string, '%b %d %Y %I:%M%p')
        if now > on_datetime:
            self._activate_objects()
        elif now > off_datetime:
            self._deactivate_objects()

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


class SimpleTimer(Timer):
    def __init__(self, on_time, off_time):
        self.on_time = parse_simple_time_string(on_time)  # type: int
        self.off_time = parse_simple_time_string(off_time)  # type: int
        super().__init__()

    def _check_timer(self):
        now = datetime.now()
        if not self.outputs_activated:
            if self.deactivated_time + timedelta(seconds=self.off_time) < now:
                self.activated_time = datetime.now()
                self._activate_objects()

        else:
            if self.activated_time + timedelta(seconds=self.on_time) < now:
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
