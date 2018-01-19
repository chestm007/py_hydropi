from datetime import datetime, timedelta
from threading import Thread
from time import sleep

from ..time_utils import parse_clock_time_string, parse_simple_time_string


def timer_factory(timer_type, params):
    if timer_type == 'clock':
        return ClockTimer(**params)
    if timer_type == 'simple':
        return SimpleTimer(**params)


class Timer(object):
    def __init__(self):
        self.attached_outputs = []
        self.attached_triggered_outputs = {}
        self.activated_time = None  # type: datetime
        self.deactivated_time = datetime.now()  # type: datetime
        self._continue = True  # set to false to exit self._timer_loop
        self.timer_thread = Thread(target=self._timer_loop())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def attach_object(self, obj):
        self.attached_outputs.append(obj)

    def _activate_objects(self):
        for output in self.attached_outputs:
            output.activate()

    def _deactivate_objects(self):
        for output in self.attached_outputs:
            output.deactivate()

    def _activate_triggered_objects(self, group_name):
        for output in self.attached_triggered_outputs[group_name]['objects']:
            output.activate()

    def _deactivate_triggered_objects(self, group_name):
        for output in self.attached_triggered_outputs[group_name]['objects']:
            output.deactivate()

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
        self.timer_thread.start()

    def stop(self):
        self._continue = False
        self.timer_thread.join()

    def _timer_loop(self):
        while self._continue:
            self._check_timer()
            self._check_after_trigger()
            self._check_before_trigger()
            sleep(0.5)


class ClockTimer(Timer):
    def __init__(self, active_hours):
        super().__init__()
        self.on_time, self.off_time = parse_clock_time_string(active_hours)

    def _check_timer(self):
        now = datetime.now().strftime('%I:%M%p').lower()
        if now == self.on_time:
            self._activate_objects()
        elif now == self.off_time:
            self._deactivate_objects()

    def _check_before_trigger(self):
        for group_name, opts in self.attached_triggered_outputs.items():
            now = datetime.now()
            on_string = now.strftime('%b %d %Y {}'.format(self.on_time))
            on_datetime = datetime.strptime(on_string, '%b %d %Y %I:%M%p')
            if on_datetime < now:
                on_datetime += timedelta(days=1)
            if on_datetime - timedelta(minutes=opts['before']) > now:
                self._activate_triggered_objects(group_name)

    def _check_after_trigger(self):
        for group_name, opts in self.attached_triggered_outputs.items():
            now = datetime.now()
            off_string = now.strftime('%b %d %Y {}'.format(self.off_time))
            off_datetime = datetime.strptime(off_string, '%b %d %Y %I:%M%p')
            if off_datetime < now:
                off_datetime += timedelta(days=1)
            if off_datetime + timedelta(minutes=opts['after']) > now:
                self._deactivate_triggered_objects(group_name)


class SimpleTimer(Timer):
    def __init__(self, on, off):
        super().__init__()
        self.on_time = parse_simple_time_string(on)  # type: int
        self.off_time = parse_simple_time_string(off)  # type: int

    def _check_timer(self):
        now = datetime.now()
        if self.deactivated_time is not None:
            if self.deactivated_time + timedelta(minutes=self.off_time) > now:
                self.activated_time = datetime.now()
                self.deactivated_time = None
                for output in self.attached_outputs:
                    output.activate()

        elif self.activated_time is not None:
            if self.activated_time + timedelta(minutes=self.on_time) > now:
                self.deactivated_time = datetime.now()
                self.activated_time = None
                for output in self.attached_outputs:
                    output.deactivate()

    def _check_before_trigger(self):
        for group_name, opts in self.attached_triggered_outputs.items():
            now = datetime.now()
            if self.deactivated_time + timedelta(minutes=self.off_time) - timedelta(minutes=opts['before']) > now:
                self._activate_triggered_objects(group_name)

    def _check_after_trigger(self):
        for group_name, opts in self.attached_triggered_outputs.items():
            now = datetime.now()
            if self.activated_time + timedelta(minutes=self.on_time) + timedelta(minutes=opts['after']) > now:
                self._deactivate_triggered_objects(group_name)
