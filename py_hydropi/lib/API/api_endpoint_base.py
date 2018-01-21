from py_hydropi.lib.API.main import ApiServer
import cherrypy


class APIEndpointBase(object):
    exposed = True

    def __init__(self, api):
        self.api = api  # type: ApiServer

    @cherrypy.tools.json_out()
    def GET(self):
        return self._get()

    def POST(self):
        return self._post()

    def PUT(self):
        return self._put()

    def DELETE(self):
        return self._delete()

    def _delete(self):
        raise cherrypy._cperror.HTTPError(405, None)

    def _put(self):
        raise cherrypy._cperror.HTTPError(405, None)

    def _post(self):
        raise cherrypy._cperror.HTTPError(405, None)

    def _get(self):
        raise cherrypy._cperror.HTTPError(405, None)
