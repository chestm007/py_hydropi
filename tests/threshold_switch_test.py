from py_hydropi.lib.modules.threshold_switch import ThresholdSwitch


class DI:
    def __init__(self, tmt):
        self.falling = True
        self._temp = 20
        self._test_moving_temp = tmt

    @property
    def temp(self):
        if self._test_moving_temp:
            print(self._temp)
            if self.falling:
                if self._temp < 15:
                    self.falling = False
                self._temp -= 0.1
                return self._temp
            if not self.falling:
                if self._temp > 25:
                    self.falling = True
                self._temp += 0.1
                return self._temp
        else:
            return 20


class DO:
    manual_control = False
    channel = 1

    def activate(self):
        print('activate m8')

    def deactivate(self):
        print('deacivate m8')


def main_test(temp_moving_target=False):
    threshold_switch = ThresholdSwitch(target=20,
                                       upper=20.3,
                                       lower=19.7,
                                       min_duty_cycle=0.33,
                                       input_=DI(tmt=temp_moving_target))
    threshold_switch.set_falling_object(DO())
    threshold_switch.set_rising_object(DO())
    threshold_switch.start()


def static_temp_test():
    main_test()


def moving_temp_test():
    main_test(True)