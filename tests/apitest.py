from py_hydropi.lib.API.main import ApiServer
from py_hydropi.main import MemDatabase


class TestConfig(object):
    self = None
    cherrypy = None
    _cpserver = None
    strict_port_checking = True
    listen_address = '0.0.0.0'
    port = 8084


def main():
    db = MemDatabase()
    db.lights = {'asd': 1}
    api = ApiServer(db)
    config = TestConfig
    api.load_config(config)
    api.start()

if __name__ == '__main__':
    main()
