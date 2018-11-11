from py_hydropi.lib.API.main import ApiServer
import cherrypy


# noinspection PyPep8Naming
class APIEndpointBase(object):
    exposed = True
    error_405 = cherrypy.HTTPError(405, None)

    def __init__(self, api):
        self.api = api  # type: ApiServer

    @cherrypy.tools.json_out()
    def GET(self):
        return self._get()

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        return self._post(cherrypy.request.json)

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self):
        return self._put(cherrypy.request.json)

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def DELETE(self):
        return self._delete(cherrypy.request.json)

    def _delete(self, *args, **kwargs):
        raise self.error_405

    def _put(self, *args, **kwargs):
        raise self.error_405

    def _post(self, *args, **kwargs):
        raise self.error_405

    def _get(self):
        raise self.error_405
