import time

from py_hydropi.lib import Output, parse_simple_time_string
from py_hydropi.lib.iter_utils import JSONableDict
from py_hydropi.lib.modules.inputs import Input
from py_hydropi.lib.modules.switch import Switch
from py_hydropi.lib.modules.timer import SimpleTimer


class ThresholdSwitch(Switch):
    RISING = 1
    FALLING = -1
    INACTIVE = 0

    def __init__(self, target: float=None, upper: float=None,
                 lower: float=None, input_: Input=None, poll_sec=1,
                 alter_target=None, rpi_timer=None):

        super().__init__()
        self.rpi_timer = rpi_timer
        self._target = target
        self._upper = upper
        self._lower = lower
        self._input = input_
        self._state = self.INACTIVE
        self._rising_object = None
        self._falling_object = None
        self._rising_activated = False
        self._falling_activated = False
        self._poll_sec = poll_sec

        if alter_target:
            altering_output = alter_target.get('output')
            altering_input = alter_target.get('input')
            self.alter_when = alter_target.get('when')
            if altering_output:
                self.altering_obj = self.rpi_timer.db.get_output(altering_output)
                self.alter_func = lambda o: (o.outputs_activated or False) == (self.alter_when == 'activated')

            elif altering_input:
                self.altering_obj = self.rpi_timer.db.get_input(sensor_id=altering_input)

                if '<' in self.alter_when:
                    self.alter_func = lambda o: o.value < float(self.alter_when.split(' ')[1])

                elif '>' in self.alter_when:
                    self.alter_func = lambda o: o.value > float(self.alter_when.split(' ')[1])

            self.alter_by = alter_target.get('alter_by')

            assert self.altering_obj
            assert self.alter_by
            assert self.alter_func

        self.threshold_timer = None

    @property
    def all_outputs(self):
        out = super().all_outputs
        out.extend([self._rising_object, self._falling_object])
        return out

    def to_json(self):
        return JSONableDict(target=self._target,
                            poll_sec=self._poll_sec,
                            upper_limit=self._upper,
                            lower_limit=self._lower)

    @staticmethod
    def factory(**kwargs):
        if kwargs.get('periodic'):
            kwargs = {k: v for k, v in kwargs.items() if k in ('target', 'upper', 'lower', 'input_',
                                                               'poll_sec', 'periodic', 'rpi_timer',
                                                               'alter_target')}
            return PeriodicThresholdSwitch(**kwargs)
        elif kwargs.get('min_duty_cycle'):
            kwargs = {k: v for k, v in kwargs.items() if k in ('target', 'upper', 'lower', 'input_',
                                                               'poll_sec', 'min_duty_cycle',
                                                               'rpi_timer', 'alter_target')}
            return TargetThresholdSwitch(**kwargs)

    @classmethod
    def load_config(cls, raspberry_pi_timer, config):
        objects = {group: cls.factory(
            target=group_settings.get('target'),
            upper=group_settings.get('upper').get('limit'),
            lower=group_settings.get('lower').get('limit'),
            min_duty_cycle=group_settings.get('min_duty_cycle'),
            input_=raspberry_pi_timer.db.get_input(sensor_id=group_settings.get('input')),
            periodic=group_settings.get('periodic'),
            alter_target=group_settings.get('alter_target'),
            rpi_timer=raspberry_pi_timer
        ).set_rising_object(
            Output(pi_timer=raspberry_pi_timer,
                   channel=group_settings.get('lower').get('channel'))
        ).set_falling_object(
            Output(pi_timer=raspberry_pi_timer,
                   channel=group_settings.get('upper').get('channel'))
        ) for group, group_settings in config.items()}
        return objects

    def set_rising_object(self, obj):
        self._rising_object = obj
        return self

    def set_falling_object(self, obj):
        self._falling_object = obj
        self.attached_outputs.append(obj)
        return self

    def _activate_rising_objects(self):
        if not self._rising_activated:
            self._rising_object.activate()
            self._rising_activated = True
            self._state = self.RISING

    def _activate_falling_objects(self):
        if not self._falling_activated:
            self._falling_object.activate()
            self._falling_activated = True
            self._state = self.FALLING

    def _deactivate_rising_objects(self):
        if self._rising_activated:
            self._rising_object.deactivate()
            self._rising_activated = False
        self._state = self.INACTIVE

    def _deactivate_falling_objects(self):
        if self._falling_activated:
            self._falling_object.deactivate()
            self._falling_activated = False
        self._state = self.INACTIVE

    def stop(self):
        if self.threshold_timer:
            self.threshold_timer.stop()
        super().stop()

    def _main_loop(self):
        while self._continue:
            if self._input.value:
                if hasattr(self, 'alter_by'):
                    self.logger.debug('pre-alter >{} <{} ={}'.format(self._upper, self._lower, self._target))
                    upper, lower, target = self._upper, self._lower, self._target
                    try:
                        if self.alter_func(self.altering_obj):
                            self._upper += self.alter_by
                            self._lower += self.alter_by
                            self._target += self.alter_by
                            self.logger.debug('post-alter >{} <{} ={}'.format(self._upper, self._lower, self._target))
                    except TypeError:
                        pass

                    self._sub_loop()
                    self._upper, self._lower, self._target = upper, lower, target
                    self.logger.debug('post-loop >{} <{} ={}'.format(self._upper, self._lower, self._target))
                else:
                    self._sub_loop()

            time.sleep(self._poll_sec)

    def _sub_loop(self):
        raise NotImplementedError


class PeriodicThresholdSwitch(ThresholdSwitch):
    def __init__(self, target=None, upper: float=None, lower: float=None, input_: Input=None,
                 poll_sec=1, periodic=None, rpi_timer=None, alter_target=None):

        super().__init__(target=target, upper=upper, lower=lower, input_=input_,
                         poll_sec=poll_sec, alter_target=alter_target, rpi_timer=rpi_timer)
        self._periodic = periodic
        self._periodic_active_sec = parse_simple_time_string(periodic.get('active'))
        self._poll_sec = parse_simple_time_string(periodic.get('inactive'))

    def _sub_loop(self):
        if self._input.value < self._lower:
            self._activate_rising_objects()
            time.sleep(self._periodic_active_sec)
            self._deactivate_rising_objects()

        if self._input.value > self._upper:
            self._activate_falling_objects()
            time.sleep(self._periodic_active_sec)
            self._deactivate_falling_objects()


class TargetThresholdSwitch(ThresholdSwitch):
    def __init__(self, target: float=None, upper: float=None,
                 lower: float=None, min_duty_cycle: float=0, input_: Input=None, poll_sec=1,
                 alter_target=None, rpi_timer=None):

        super().__init__(target=target, upper=upper, lower=lower, input_=input_,
                         poll_sec=poll_sec, alter_target=alter_target, rpi_timer=rpi_timer)
        self.rpi_timer = rpi_timer
        self._min_duty_cycle = min_duty_cycle

    def _sub_loop(self):
        if self._state == self.FALLING:
            if self._input.value <= self._target:
                self._deactivate_falling_objects()
        else:
            if self._min_duty_cycle and not self.threshold_timer:
                self.threshold_timer = SimpleTimer(
                    '{}s'.format(int(60 * self._min_duty_cycle)),
                    '{}s'.format(int(60 - (60 * self._min_duty_cycle))))
                self.threshold_timer.attached_outputs.append(self._falling_object)
                self.threshold_timer.start()

            if self._state == self.INACTIVE:
                if self._input.value > self._upper:
                    if self._min_duty_cycle and self.threshold_timer:
                        self.threshold_timer.stop()
                        self.threshold_timer = None

                    self._activate_falling_objects()

                elif self._input.value < self._lower:
                    self._activate_rising_objects()

            elif self._state == self.RISING:
                if self._input.value >= self._target:
                    self._deactivate_rising_objects()
