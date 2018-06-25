import os

import time

import requests


class InfluxDBClient:
    def __init__(self, endpoint="127.0.0.1", port=8086, hostname=None, db='py_hydropi'):
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

    def push(self, metric, value):
        payload = "{metric},host={hostname} value={value} {timestamp}00".format(
            metric=metric,
            hostname=self.hostname,
            value=value,
            timestamp=self._get_current_timestamp()
        )
        res = requests.post(url='http://{}:{}/write?db={}'.format(self.endpoint, self.port, self.db),
                            data=payload,
                            headers={'Content-Type': 'application/octet-stream'})
        print(res)