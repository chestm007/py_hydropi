import logging

import os
from systemd import journal


# noinspection PyUnusedLocal
class Logger(object):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

    def __init__(self, obj, debug=False):
        if os.environ.get('PY_HYDROPI_LOGGING'):
            env_level = os.environ.get('PY_HYDROPI_LOGGING')
            if env_level:
                self.level = getattr(self, env_level)

            class ScreenLogger(logging.Logger):
                warning = print
                info = print
                error = print
                debug = print
            self._logger = ScreenLogger(obj)
        else:
            self._logger = logging.getLogger(obj)
            if not self._logger.handlers:
                self._logger.addHandler(journal.JournaldLogHandler())
        if debug:
            self.level = self.DEBUG
        self._logger.setLevel(self.level or self.INFO)
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

