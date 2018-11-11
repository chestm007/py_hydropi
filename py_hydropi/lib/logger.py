import logging

import os
from systemd import journal


# noinspection PyUnusedLocal
class Logger(object):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

    def __init__(self, obj):
        if os.environ.get('PY_HYDROPI_TESTING', '').lower() == 'true':
            class ScreenLogger(logging.Logger):
                def error(self, msg, *args, **kwargs):
                    if self.level <= Logger.ERROR:
                        print(msg.format(*args, **kwargs))

                def warning(self, msg, *args, **kwargs):
                    if self.level <= Logger.WARNING:
                        print(msg.format(*args, **kwargs))

                def debug(self, msg, *args, **kwargs):
                    if self.level <= Logger.DEBUG:
                        print(msg.format(*args, **kwargs))

                def info(self, msg, *args, **kwargs):
                    if self.level <= Logger.INFO:
                        print(msg.format(*args, **kwargs))

            self._logger = ScreenLogger(obj)
        else:
            self._logger = logging.getLogger(obj)
            if not self._logger.handlers:
                self._logger.addHandler(journal.JournaldLogHandler())

        env_level = os.environ.get('PY_HYDROPI_LOGGING', '').upper() or 'INFO'
        level = getattr(self, env_level) or self.INFO
        self._logger.setLevel(level)

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
