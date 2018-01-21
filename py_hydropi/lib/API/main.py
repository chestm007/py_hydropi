import cherrypy
import os

from py_hydropi.lib.memdatabase import MemDatabase

from ..logger import Logger
from cherrypy import _cpwsgi_server, _cpserver


class ApiServer(object):
    def __init__(self, db, service_name='cherrypy'):
        self.logger = Logger(service_name)
        self.is_running = False
        self.strict_port_checking = False
        self.adapter = None  # type: _cpserver.ServerAdapter
        self.logger = Logger('api')
        self.cherrypy_server = _cpwsgi_server.CPWSGIServer()
        self.db = db  # type: MemDatabase

    def start(self):
        if self.is_running:
            return
        # hackery to stop cherrypy outputting log to stdout (spams journald when ran
        # in the foreground as a systemd service. all logs from cherrypy will now be
        # routed to syslog instead (journal if running systemd)
        cherrypy.log.screen = False
        cherrypy.log.error_log.log = self.logger.log
        cherrypy.log.error_log.propagate = False
        cherrypy._cpchecker.Checker.on = False  # stops cherrypy checking for config
        cherrypy.engine.signals.subscribe()
        cherrypy.engine.start()
        cherrypy.log.access_log.log = self.logger.log
        cherrypy.log.access_log.propagate = False
        self.is_running = True

    def stop(self):
        if self.is_running:
            cherrypy.engine.exit()
            self.is_running = False

    def load_config(self, config):
        self.strict_port_checking = config.strict_port_checking
        self.cherrypy_server.bind_addr = (config.listen_address,
                                          config.port)
        self.lazy_load_endpoints()
        self.adapter = _cpserver.ServerAdapter(cherrypy.engine,
                                               self.cherrypy_server,
                                               self.cherrypy_server.bind_addr)
        self.adapter.subscribe()

    def lazy_load_endpoints(self, endpoint_dir=None):
        if endpoint_dir is None:
            endpoint_dir = (os.path.join(os.path.dirname(os.path.realpath(__file__)), 'endpoints'))
        for found in os.listdir(endpoint_dir):
            dir = os.path.join(endpoint_dir, found)
            if found != '__init__.py':
                if os.path.isdir(dir):
                    self.lazy_load_endpoints(dir)
                else:
                    endpoint = '/' + str(dir.split('endpoints/')[1].replace(found, ''))
                    imp_dir = 'py_hydropi' + str(dir).split('py_hydropi')[2].replace('/', '.').replace('.py', '')
                    module = __import__(str(imp_dir), fromlist=[found])
                    found = ''.join([str(i.capitalize()) for i in found.replace('.py', '').split('_')])
                    class_ = getattr(module, found)
                    instance = class_(self)
                    cherrypy.tree.mount(instance, endpoint,
                                        {
                                            '/': {
                                                'request.dispatch': cherrypy.dispatch.MethodDispatcher()}})

