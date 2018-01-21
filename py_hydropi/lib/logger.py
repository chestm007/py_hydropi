class Logger(object):
    def __init__(self, obj):
        self.calling_obj = obj

    def warn(self, msg, *args, **kwargs):
        print('{}: WARNING: {}'.format(self.calling_obj, msg))
        print(args, kwargs)

    def info(self, msg, *args, **kwargs):
        print('{}: INFO: {}'.format(self.calling_obj, msg))
        print(args, kwargs)

    def log(self, msg, *args, **kwargs):
        print('{}: {}'.format(self.calling_obj, msg))
        print(args, kwargs)
