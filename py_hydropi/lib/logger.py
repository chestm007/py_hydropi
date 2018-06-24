import logging


# noinspection PyUnusedLocal
class Logger(object):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

    def __init__(self, obj):
        self.calling_obj = obj

    def warn(self, msg, *args, **kwargs):
        print('{}: WARNING: {}'.format(self.calling_obj, msg))

    def info(self, msg, *args, **kwargs):
        print('{}: INFO: {}'.format(self.calling_obj, msg))

    def error(self, msg, *args, **kwargs):
        print('{}: ERROR: {}'.format(self.calling_obj, msg))

    def _log(self, msg):
        print('{}: LOG: {}'.format(self.calling_obj, msg))

    def log(self, level, msg, *args, **kwargs):
        if level == self.INFO:
            self._log(msg)

        if level == self.DEBUG:
            self.info(msg)

        if level == self.WARNING:
            self.warn(msg)

        if level == self.ERROR:
            self.error(msg)

