import json

from sanic.server import HttpProtocol
from sanic.log import logger, access_logger
from sanic.response import HTTPResponse
from sanic.handlers import ErrorHandler


from traceback import format_exc
from sanic.exceptions import INTERNAL_SERVER_ERROR_HTML, SanicException
from sanic.response import text, html


class PGHttpProtocol(HttpProtocol):

    def log_response(self, response):
        if self.access_log:
            extra = {
                'status': getattr(response, 'status', 0),
            }
            if isinstance(response, HTTPResponse):
                extra['byte'] = len(response.body)
            else:
                extra['byte'] = -1
            extra['host'] = 'UNKNOWN'
            if self.request is not None:
                if self.request.ip:
                    extra['host'] = '{0[0]}:{0[1]}'.format(self.request.ip)

                req_base = '{0} {1}'.format(self.request.method,
                                                    self.request.url)
                req_from = self.request.remote_addr if self.request.remote_addr else "client"
                extra['request'] = f"{req_from} --->> {req_base}"
            else:
                extra['request'] = 'nil'

            access_logger.info('', extra=extra)
            if self.request.app.config.LOG_INCOMING_REQUEST:
                if self.request.method == "POST":
                    from pprint import pprint
                    print(self.request.headers)
                    pprint(self.request.json)
                    print(self.request.body)
            logger.info("------")


class PGErrorHandler(ErrorHandler):

    def default(self, request, exception):
        if not getattr(exception, 'status_code', None) == 404:
            self.log(format_exc())

        if issubclass(type(exception), SanicException):
            return text(
                'Error: {}'.format(exception),
                status=getattr(exception, 'status_code', 500),
                headers=getattr(exception, 'headers', dict())
            )
        elif self.debug:
            html_output = self._render_traceback_html(exception, request)

            response_message = ('Exception occurred while handling uri: '
                                '"%s"\n%s')
            logger.error(response_message, request.url, format_exc())
            return html(html_output, status=500)
        else:
            return html(INTERNAL_SERVER_ERROR_HTML, status=500)