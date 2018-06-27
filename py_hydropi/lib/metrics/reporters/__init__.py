from py_hydropi.lib.metrics.reporters.influxdb import InfluxDBClient


def reporter_factory(config):
    c = config.get('influxdb')
    if c:
        return InfluxDBClient(**c)
