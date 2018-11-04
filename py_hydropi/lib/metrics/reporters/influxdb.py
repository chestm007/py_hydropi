import time

import requests

from py_hydropi.lib.logger import Logger


SUCCESS = 204


class InfluxDBClient:
    def __init__(self, endpoint="127.0.0.1", port=8086, hostname=None, db='py_hydropi'):
        self.logger = Logger(self.__class__.__name__)
        self.endpoint = endpoint
        self.port = port
        self.hostname = hostname or self._get_hostname()
        self.db = db

    @staticmethod
    def _get_hostname():
        with open('/etc/hostname') as f:
            return f.read()

    @staticmethod
    def _get_current_timestamp():
        return str(time.time()).replace('.', '')

    def push(self, callback, metric, value):
        self.logger.debug('metric: {}, value: {}'.format(metric, value))
        if value is not None:
            payload = "{metric},host={hostname} value={value} {timestamp}00".format(
                metric=metric,
                hostname=self.hostname,
                value=value,
                timestamp=self._get_current_timestamp()
            )
            result = requests.post(url='http://{}:{}/write?db={}'.format(self.endpoint, self.port, self.db),
                                   data=payload,
                                   headers={'Content-Type': 'application/octet-stream'})
            if result.status_code != SUCCESS:
                callback([result.status_code, result.reason])

