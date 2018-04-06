import logging

from logging.handlers import StreamHandler

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from iopipe.signer import get_signed_request

from .request import upload_log_data


class LoggingPlugin(object):
    name = 'logging'
    version = '0.1.0'
    homepage = 'https://github.com/iopipe/iopipe-python#logging-plugin'
    enabled = True

    def __init__(self, level=logging.INFO, formatter=None, name=None):
        """
        Instantiates the logging plugin

        :param level: Specify a log level for the handler.
        :param formatter: Specify a custom log message formatter.
        :param name: Specify custom log name.
        """
        if formatter is None:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.handler = StreamHandler(StringIO())
        self.handler.setFormatter(formatter)
        self.handler.setLevel(level)

        self.logger = logging.getLogger(name)
        self.logger.addHandler(self.handler)

    def pre_setup(self, iopipe):
        pass

    def post_setup(self, iopipe):
        if iopipe.config['debug'] is True:
            self.handler.setLevel(logging.DEBUG)

    def pre_invoke(self, event, context):
        self.handler.stream = StringIO()

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
