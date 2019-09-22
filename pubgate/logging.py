import json

from sanic.server import HttpProtocol
from sanic.log import logger, access_logger
from sanic.response import HTTPResponse
from sanic.handlers import ErrorHandler


from traceback import format_exc, print_exc
from sanic.exceptions import INTERNAL_SERVER_ERROR_HTML, SanicException
from sanic.response import text, html


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
            return text(
                {'error': '{}'.format(exception)},
                status=getattr(exception, 'status_code', 500),
                headers=getattr(exception, 'headers', dict())
            )
        # elif self.debug:
        #     html_output = self._render_traceback_html(exception, request)
        #
        #     response_message = ('Exception occurred while handling uri: '
        #                         '"%s"\n%s')
        #     logger.error(response_message, request.url, format_exc())
        #     return html(html_output, status=500)
        else:
            print_exc()
            return html(INTERNAL_SERVER_ERROR_HTML, status=500)
