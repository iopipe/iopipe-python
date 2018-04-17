import logging
import sys
import tempfile

from iopipe.compat import StringIO
from iopipe.plugins import Plugin
from iopipe.signer import get_signed_request

from .formatter import JSONFormatter
from .request import upload_log_data
from .stream import StreamToLogger
from .wrapper import LogWrapper


class LoggerPlugin(Plugin):
    name = 'logger'
    version = '0.1.0'
    homepage = 'https://github.com/iopipe/iopipe-python#logger-plugin'
    enabled = True

    def __init__(self, name=None, level=logging.INFO, redirect_stdout=True, use_tmp=False):
        """
        Instantiates the logger plugin

        :param name: Specify custom log name.
        :type name: str
        :param level: Specify a log level for the handler.
        :type level: int
        :param redirect_stdout: Whether or not to redirect stdout.
        :type redirect_print: bool
        :param use_tmp: Write logs to the /tmp directory instead of a memory buffer.
        :type use_tmp: bool
        """
        formatter = JSONFormatter()

        self.handler = logging.StreamHandler(StringIO())
        self.handler.setFormatter(formatter)
        self.handler.setLevel(level)

        self.logger = logging.getLogger(name)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(level)

        self.redirect_stdout = redirect_stdout
        self.use_tmp = use_tmp

    def pre_setup(self, iopipe):
        pass

    def post_setup(self, iopipe):
        if iopipe.config['debug'] is True:
            self.handler.setLevel(logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)

    def pre_invoke(self, event, context):
        context.iopipe.register('log', LogWrapper(self.logger, context), force=True)

        if self.use_tmp is True:
            self.handler.stream = tempfile.NamedTemporaryFile(mode='w')
        else:
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
                if self.use_tmp is True:
                    self.handler.stream.close()

    def __del__(self):
        if self.use_tmp and self.handler and self.handler.stream:
            self.handler.stream.close()
