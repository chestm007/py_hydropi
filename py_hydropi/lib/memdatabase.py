class MemDatabase(object):
    def __init__(self):
        self.lights = {}       # {'group_name': [Output(), Output(), ...]}
        self.air_pumps = {}    # {'group_name': [Output(), Output(), ...]}
        self.water_pumps = {}  # {'group_name': [Output(), Output(), ...]}
        self.groups = []       # ['group_name', 'group_name', ...]
        self.timers = {}       # {'output_type.group_name': Timer()}


