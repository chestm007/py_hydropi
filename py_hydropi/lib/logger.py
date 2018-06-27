import logging
from systemd import journal


# noinspection PyUnusedLocal
class Logger(object):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

    def __init__(self, obj, debug=False):
        self._logger = logging.getLogger(obj)
        if not self._logger.handlers:
            self._logger.addHandler(journal.JournaldLogHandler())
        self._logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.calling_obj = obj

    def warn(self, msg, *args, **kwargs):
        self._logger.warning('{}: WARNING: {}'.format(self.calling_obj, msg))

    def info(self, msg, *args, **kwargs):
        self._logger.info('{}: INFO: {}'.format(self.calling_obj, msg))

    def error(self, msg, *args, **kwargs):
        self._logger.error('{}: ERROR: {}'.format(self.calling_obj, msg))

    def debug(self, msg, *args, **kwargs):
        self._logger.debug('{}: DEBUG: {}'.format(self.calling_obj, msg))

    def log(self, level, msg, *args, **kwargs):
        if level == self.INFO:
            self.info(msg)

        if level == self.DEBUG:
            self.debug(msg)

        if level == self.WARNING:
            self.warn(msg)

        if level == self.ERROR:
            self.error(msg)

