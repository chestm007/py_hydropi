import pprint
from multiprocessing import Queue

from py_hydropi.lib.config import ApiConfig
from py_hydropi.lib.memdatabase import MemDatabase
from py_hydropi.lib.modules.inputs import Input
from py_hydropi.lib.modules.threshold_switch import ThresholdSwitch

from .lib.API.main import ApiServer

from .lib import Logger, Output, timer_factory, ModuleConfig, GPIO


class RaspberryPiTimer(object):
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.gpio = GPIO()
        self.module_config = ModuleConfig()
        self.api_config = ApiConfig()
        self.queue = Queue()
        self.db = MemDatabase(self.queue)
        self.db.gpio = self.gpio
        if self.api_config.start:
            self.api = ApiServer(self.db, self.api_config)
        self.setup_outputs()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def cleanup(self):
        self.gpio.cleanup()

    def start(self):
        if hasattr(self, 'api'):
            self.api.start()
        for timer in self.db.timers.values():
            timer.start()
        for c in self.db.controllers.values():
            c.start()
        self._queue_loop()

    def _queue_loop(self):
        while True:
            try:
                recv_req = self.queue.get()
                if recv_req == 'exit':
                    self.logger.info('recieved exit command. shutting down services.')
                    break
            except KeyboardInterrupt:
                self.logger.info('Detected KeyboardInterupt in queue loop, exiting gracefully')
                self.stop()

    def stop(self):
        if hasattr(self, 'api'):
            self.api.stop()
        for timer in self.db.timers.values():
            self.logger.info('Stopping timer for {}'.format(''.join(timer.to_json())))
            timer.stop()
        self.cleanup()

    def _experimental_setup_outputs(self):
        groups = {}
        for name, group in self.module_config.groups.items():
            groups[name] = []
            for obj_type in ('lights', 'water_pumps', 'air_pumps'):
                output_group = {}
                output_type = group.get(obj_type)
                if output_type:
                    output_group['outputs'] = [
                        Output(gpio=self.gpio, channel=channel) for channel in output_type.get('channels')
                    ]
                    schedule = output_type.get('schedule')
                    output_group['timer'] = timer_factory(''.join(schedule.keys()), **schedule.get(''.join(schedule.keys())))
                groups[name].append(output_group)
        print = pprint.pprint
        print(groups)

    def _setup_outputs(self):
        triggers = []
        for obj_type in ('lights', 'water_pumps', 'air_pumps'):
            self.logger.info('loading {}'.format(obj_type))
            if hasattr(self.module_config, obj_type):
                mod_conf = getattr(self.module_config, obj_type)
                if not mod_conf:
                    continue
                for group in mod_conf.keys():
                    group_outputs = []
                    if group not in self.db.groups:
                        self.db.groups.append(group)
                    for channel in getattr(self.module_config, obj_type).get(group).get('channels'):
                        output = Output(gpio=self.gpio, channel=channel)
                        group_outputs.append(output)
                        if getattr(self.db, obj_type).get(group) is not None:
                            getattr(self.db, obj_type).get(group).append(output)
                        else:
                            getattr(self.db, obj_type)[group] = [output]
                    schedule = getattr(self.module_config, obj_type).get(group).get('schedule')

                    if ''.join(schedule.keys()) != 'trigger':
                        timer = timer_factory(''.join(schedule.keys()), **schedule.get(''.join(schedule.keys())))
                        for output in group_outputs:
                            timer.attach_object(output)
                        self.db.timers[obj_type + '.' + group] = timer
                    else:
                        triggers.append(
                            {
                                schedule.get(''.join(schedule.keys())).get('object'):
                                    {
                                        'before': schedule.get(''.join(schedule.keys())).get('before'),
                                        'after': schedule.get(''.join(schedule.keys())).get('after'),
                                        'output_type': obj_type,
                                        'group': group,
                                        'outputs': group_outputs
                                    }
                            })
        threshold_config = self.module_config.config.get('threshold')
        if threshold_config is not None:
            for group, group_settings in threshold_config.items():
                self.db.controllers[group] = ThresholdSwitch(
                    target=group_settings.get('target'),
                    upper=group_settings.get('upper').get('limit'),
                    lower=group_settings.get('lower').get('limit'),
                    min_duty_cycle=group_settings.get('min_duty_cycle'),
                    input_=Input(group_settings.get('input')).start()
                ).set_rising_object(
                    Output(gpio=self.gpio,
                           channel=group_settings.get('lower').get('channel'))
                ).set_falling_object(
                    Output(gpio=self.gpio,
                           channel=group_settings.get('upper').get('channel'))
                )

        attached_triggers = []
        while True:
            prev_trigger_len = len(triggers)
            for i, trigger_dict in enumerate(triggers):
                for group, trigger in trigger_dict.items():
                    group = ''.join(trigger_dict.keys())
                    related_timer = self.db.timers.get(group)
                    if related_timer:
                        for output in trigger.get('outputs'):
                            related_timer.attach_triggered_object(
                                obj=output,
                                group_name=trigger.get('output_type') + '.' + trigger.get('group'),
                                before=trigger.get('before'),
                                after=trigger.get('after'))
                        attached_triggers.append(trigger_dict)
            for trigger in attached_triggers:
                triggers.remove(trigger)
            if len(triggers) == prev_trigger_len:
                self.logger.warn(
                    'not all trigger schedules were consumed. unconsumed objects are \n{}'
                    .format(triggers))
                break

            if len(triggers) == 0:
                break

    setup_outputs = _setup_outputs


def main():
    rpi_timer = RaspberryPiTimer()
    rpi_timer.start()
    rpi_timer.stop()
    rpi_timer.cleanup()


if __name__ == '__main__':
    main()
