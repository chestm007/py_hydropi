import time

from py_hydropi.lib import Output
from py_hydropi.lib.modules.inputs import Input
from py_hydropi.lib.modules.switch import Switch
from py_hydropi.lib.modules.timer import SimpleTimer


class ThresholdSwitch(Switch):
    RISING = 1
    FALLING = -1
    INACTIVE = 0

    poll_sec = 1

    def __init__(self, target: float=None, upper: float=None,
                 lower: float=None, min_duty_cycle: float=0, input_: Input=None):

        super(ThresholdSwitch, self).__init__()
        self._target = target
        self._upper = upper
        self._lower = lower
        self._min_duty_cycle = min_duty_cycle
        self._input = input_
        self._state = self.INACTIVE
        self._rising_object = None
        self._falling_object = None
        self._rising_activated = False
        self._falling_activated = False
        self.threshold_timer = None
        #self._modify_triggers

    @classmethod
    def load_config(cls, raspberry_pi_timer, config):
        return {group: cls(
            target=group_settings.get('target'),
            upper=group_settings.get('upper').get('limit'),
            lower=group_settings.get('lower').get('limit'),
            min_duty_cycle=group_settings.get('min_duty_cycle'),
            input_=raspberry_pi_timer.db.get_input(sensor_id=group_settings.get('input'))
        ).set_rising_object(
            Output(pi_timer=raspberry_pi_timer,
                   channel=group_settings.get('lower').get('channel'))
        ).set_falling_object(
            Output(pi_timer=raspberry_pi_timer,
                   channel=group_settings.get('upper').get('channel'))
        ) for group, group_settings in config.items()}

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
        self.threshold_timer.stop()
        super(ThresholdSwitch, self).stop()

    def _main_loop(self):
        while self._continue:
            if self._state == self.FALLING:
                if self._input.temp <= self._target:
                    self._deactivate_falling_objects()
            else:
                if not self.threshold_timer:
                    self.threshold_timer = SimpleTimer(
                        '{}s'.format(int(60*self._min_duty_cycle)),
                        '{}s'.format(int(60 - (60*self._min_duty_cycle))))
                    self.threshold_timer.attached_outputs.append(self._falling_object)
                    self.threshold_timer.start()

                if self._state == self.INACTIVE:
                    if self._input.temp > self._upper:
                        if self.threshold_timer:
                            self.threshold_timer.stop()
                            self.threshold_timer = None

                        self._activate_falling_objects()

                    elif self._input.temp < self._lower:
                        self._activate_rising_objects()

                elif self._state == self.RISING:
                    if self._input.temp >= self._target:
                        self._deactivate_rising_objects()

            time.sleep(self.poll_sec)
