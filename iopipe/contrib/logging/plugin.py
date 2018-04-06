import io
import logging

from logging.handlers import StreamHandler

from iopipe.signer import get_signed_request

from .request import upload_log_data


class LoggingPlugin(object):
    name = 'logging'
    version = '0.1.0'
    homepage = 'https://github.com/iopipe/iopipe-python#trace-plugin'
    enabled = True

    def __init__(self, log_level=logging.INFO, formatter=None, name=None):
        self.formatter = formatter
        if self.formatter is None:
            self.formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

        self.log_level = log_level
        self.logger = logging.getLogger(name)

    def pre_setup(self, iopipe):
        self.iopipe = iopipe

    def post_setup(self, iopipe):
        pass

    def pre_invoke(self, event, context):
        self.handler = StreamHandler(io.StringIO())
        self.handler.setFormatter(self.formatter)
        self.handler.setLevel(self.log_level)
        self.logger.addHandler(self.handler)

    def post_invoke(self, event, context):
        self.handler.flush()

    def pre_report(self, report):
        pass

    def post_report(self, report):
                signed_request = get_signed_request(report, '.log')
                if signed_request and 'signedRequest' in signed_request:
                    upload_log_data(signed_request['signedRequest'], self.handler.stream)
                    if 'jwtAccess' in signed_request:
                        plugin = next((p for p in report.plugins if p['name'] == self.name))
                        if 'uploads' not in plugin:
                            plugin['uploads'] = []
                        plugin['uploads'].append(signed_request['jwtAccess'])
