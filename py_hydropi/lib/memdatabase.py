class MemDatabase(object):
    def __init__(self, queue):
        self.lights = {}       # {'group_name': [Output(), Output(), ...]}
        self.air_pumps = {}    # {'group_name': [Output(), Output(), ...]}
        self.water_pumps = {}  # {'group_name': [Output(), Output(), ...]}
        self.groups = []       # ['group_name', 'group_name', ...]
        self.timers = {}       # {'output_type.group_name': Timer()}
        self.controllers = {}
        self.gpio = None
        self.server_queue = queue

    def __getattr__(self, item):
        if item == 'outputs':
            outputs = {}
            for group in self.groups:
                outputs[group] = []
                for category in ('lights', 'water_pumps', 'air_pumps'):
                    for o in getattr(self, category).get(group):
                        outputs[group].append(o)
            return outputs
        if item == 'channel':
            return self._get_output_by_channel
        else:
            super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in ('outputs', 'channels'):
            raise KeyError
        else:
            super().__setattr__(key, value)

    def _get_output_by_channel(self, channel):
        for group, outputs in self.outputs.items():
            for output in outputs:
                if int(output.channel) == int(channel):
                    return output


