class Logger(object):
    def __init__(self, obj):
        self.calling_obj = obj

    def warn(self, msg):
        print('{}: WARNING: {}'.format(self.calling_obj, msg))

    def info(self, msg):
        print('{}: INFO: {}'.format(self.calling_obj, msg))

    def log(self, msg):
        print('{}: {}'.format(self.calling_obj, msg))