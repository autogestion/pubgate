from sanic.server import HttpProtocol
from sanic.log import logger, access_logger
from sanic.response import HTTPResponse
from sanic.handlers import ErrorHandler

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
            logger.info(self.request.headers)
            logger.info("------")
