import json

from sanic.server import HttpProtocol
from sanic.handlers import ErrorHandler


from traceback import print_exc
from sanic.exceptions import SanicException
from sanic.response import json


class PGHttpProtocol(HttpProtocol):

    def log_response(self, response):
        super().log_response(response)
        if self.access_log:
            if self.request.app.config.LOG_INCOMING_REQUEST:
                if response.status != 401:
                    from pprint import pprint
                    print(self.request.headers)
                    pprint(self.request.json)
                    # print(self.request.body)
                    # logger.info("------")


class PGErrorHandler(ErrorHandler):

    def default(self, request, exception):
        if issubclass(type(exception), SanicException):
            return json(
                {'error': '{}'.format(exception)},
                status=getattr(exception, 'status_code', 500),
                headers=getattr(exception, 'headers', dict())
            )

        else:
            print_exc()
            if self.debug:
                error = {'error': '{}'.format(exception)},
            else:
                error = {'error': 'internal server error'},

            return json(
                error,
                status=getattr(exception, 'status_code', 500),
                headers=getattr(exception, 'headers', dict())
            )
