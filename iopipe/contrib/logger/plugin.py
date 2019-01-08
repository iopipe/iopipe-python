from concurrent.futures import Future, wait
from distutils.util import strtobool
import logging
import os
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
    name = "logger"
    version = "0.1.0"
    homepage = "https://github.com/iopipe/iopipe-python#logger-plugin"

    def __init__(
        self,
        name=None,
        level=logging.INFO,
        enabled=True,
        redirect_stdout=True,
        use_tmp=False,
    ):
        """
        Instantiates the logger plugin

        :param name: Specify custom log name.
        :type name: str
        :param level: Specify a log level for the handler.
        :type level: int
        :param enabled: Whether or not to enable the plugin.
        :type enabled: bool
        :param redirect_stdout: Whether or not to redirect stdout.
        :type redirect_print: bool
        :param use_tmp: Write logs to the /tmp directory instead of a memory buffer.
        :type use_tmp: bool
        """
        self._enabled = enabled
        self.redirect_stdout = redirect_stdout
        self.use_tmp = use_tmp

        if self.enabled:
            formatter = JSONFormatter()

            self.handler = logging.StreamHandler(StringIO())
            self.handler.setFormatter(formatter)
            self.handler.setLevel(level)

            self.logger = logging.getLogger(name)
            self.logger.addHandler(self.handler)
            self.logger.setLevel(level)

    @property
    def enabled(self):
        return self._enabled is True or bool(
            strtobool(os.getenv("IOPIPE_LOGGER_ENABLED", "false"))
        )

    def pre_setup(self, iopipe):
        self.iopipe = iopipe

    def post_setup(self, iopipe):
        if self.enabled and iopipe.config["debug"] is True:
            self.handler.setLevel(logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)

    def pre_invoke(self, event, context):
        self.context = context
        self.signed_request = None

        if self.enabled:
            self.signed_request = self.iopipe.submit_future(
                get_signed_request, self.iopipe.config, self.context, ".log"
            )

            self.context.iopipe.register(
                "log", LogWrapper(self.logger, context), force=True
            )

            if self.use_tmp is True:
                self.handler.stream = tempfile.NamedTemporaryFile(
                    delete=False, mode="w"
                )
            else:
                self.handler.stream = StringIO()

            if self.redirect_stdout is True:
                sys.stdout = StreamToLogger(self.logger)

    def post_invoke(self, event, context):
        if self.enabled:
            self.handler.flush()

            if self.redirect_stdout is True:
                sys.stdout = sys.__stdout__

    def pre_report(self, report):
        if self.enabled and self.handler.stream.tell():
            stream = self.handler.stream

            if hasattr(stream, "getvalue"):
                stream = StringIO(stream.getvalue())

            if hasattr(stream, "file"):
                stream = stream.name
                self.handler.stream.close()
            if self.signed_request is not None:

                if isinstance(self.signed_request, Future):
                    wait([self.signed_request])
                    self.signed_request = self.signed_request.result()

            if (
                self.signed_request is not None
                and "signedRequest" in self.signed_request
            ):
                self.iopipe.submit_future(
                    upload_log_data,
                    self.signed_request["signedRequest"],
                    stream,
                    self.iopipe.config,
                )
                if "jwtAccess" in self.signed_request:
                    plugin = next((p for p in report.plugins if p["name"] == self.name))

                    if "uploads" not in plugin:
                        plugin["uploads"] = []
                    plugin["uploads"].append(self.signed_request["jwtAccess"])

    def post_report(self, report):
        pass
