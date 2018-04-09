import logging
import sys

from logging import Formatter, StreamHandler

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from iopipe.plugins import Plugin
from iopipe.signer import get_signed_request

from .request import upload_log_data
from .stream import StreamToLogger
from .wrapper import LogWrapper


class LoggingPlugin(Plugin):
    name = 'logging'
    version = '0.1.0'
    homepage = 'https://github.com/iopipe/iopipe-python#logging-plugin'
    enabled = True

    def __init__(self, name=None, level=logging.INFO, formatter=None, redirect_stdout=True):
        """
        Instantiates the logging plugin

        :param name: Specify custom log name.
        :type name: str
        :param level: Specify a log level for the handler.
        :type level: int
        :param formatter: Specify a custom log message formatter.
        :type formatter: :class:`Formatter`
        :param redirect_stdout: Whether or not to redirect stdout.
        :type redirect_print: bool
        """
        if formatter is None or not isinstance(formatter, Formatter):
            formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.handler = StreamHandler(StringIO())
        self.handler.setFormatter(formatter)
        self.handler.setLevel(level)

        self.logger = logging.getLogger(name)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(level)

        self.redirect_stdout = redirect_stdout

    def pre_setup(self, iopipe):
        pass

    def post_setup(self, iopipe):
        if iopipe.config['debug'] is True:
            self.handler.setLevel(logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)

    def pre_invoke(self, event, context):
        context.iopipe.register('log', LogWrapper(self.logger, context), force=True)
        self.handler.stream = StringIO()

        if self.redirect_stdout is True:
            sys.stdout = StreamToLogger(self.logger)

    def post_invoke(self, event, context):
        self.handler.flush()

        if self.redirect_stdout is True:
            sys.stdout = sys.__stdout__

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
