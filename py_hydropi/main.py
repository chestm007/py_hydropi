from multiprocessing import Queue

from py_hydropi.lib.config import ApiConfig
from py_hydropi.lib.memdatabase import MemDatabase

from .lib.API.main import ApiServer

from .lib import Logger, Output, timer_factory, ModuleConfig, GPIO


class RaspberryPiTimer(object):
    logger = Logger('RaspberryPiTimer')

    def __init__(self):
        self.gpio = GPIO()
        self.module_config = ModuleConfig()
        self.api_config = ApiConfig()
        self.queue = Queue()
        self.db = MemDatabase()
        self.Api = ApiServer(self.db)
        self.Api.load_config(self.api_config)
        self.Api.start()
        self.setup_outputs()
        for timer in self.db.timers.values():
            timer.start()
        while True:
            try:
                recv_req = self.queue.get()
                if recv_req == 'exit':
                    self.logger.log('recieved exit command. shutting down services.')
                    break
            except KeyboardInterrupt:
                self.logger.log('Detected KeyboardInterupt in queue loop, exiting gracefully')
                for timer in self.db.timers:
                    timer.stop()

        for timer in self.db.timers.values():
            self.logger.log('Stopping timer for {}'.format(''.join(timer.keys())))
            timer.stop()

    def __exit__(self, exc_type, exc_val, exc_tb):
        for timer in self.db.timers:
            timer.stop()

    def setup_outputs(self):
        triggers = []
        for obj_type in ('lights', 'water_pumps', 'air_pumps'):
            if hasattr(self.module_config, obj_type):
                for group in getattr(self.module_config, obj_type).keys():
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


def main():
    rpi_timer = RaspberryPiTimer()


if __name__ == '__main__':
    main()