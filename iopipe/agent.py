import concurrent.futures as futures
import functools
import inspect
import logging
import warnings

from .config import set_config
from .context import ContextWrapper
from .plugins import is_plugin
from .report import Report
from .timeout import Timeout, TimeoutError

logging.basicConfig()

logger = logging.getLogger("iopipe")
logger.setLevel(logging.INFO)


class MockFuture(object):
    def __init__(self, func, *args, **kwargs):
        self._result = func(*args, **kwargs)

    def result(self):
        return self._result


class IOpipeCore(object):
    """
    The stock IOpipe agent, without any plugins loaded.
    """

    pool = None

    def __init__(self, token=None, url=None, debug=None, plugins=None, **options):
        self.plugins = []
        if plugins is not None and isinstance(plugins, list):
            self.plugins = self.load_plugins(plugins)
            options["plugins"] = self.plugins

        self.run_hooks("pre:setup")

        if token is not None:
            options["token"] = token
        if url is not None:
            options["url"] = url
        if debug is not None:
            options["debug"] = debug

        self.config = set_config(**options)
        self.config["plugins"] = self.load_plugins(self.config["plugins"])
        self.futures = []
        self.pool = futures.ThreadPoolExecutor()
        self.report = None

        if self.config["debug"]:
            logger.setLevel(logging.DEBUG)

        self.run_hooks("post:setup")

    def __del__(self):
        if self.pool:
            self.pool.shutdown()

    def log(self, key, value):
        if self.report is None:
            warnings.warn(
                "Attempting to log metrics before function decorated with IOpipe. "
                "This metric will not be recorded."
            )
            return

        self.report.context.iopipe.log(key, value)

    def error(self, error):
        if self.report is None:
            warnings.warn(
                "An exception occurred before function was decorated with IOpipe. "
                "This exception will not be recorded."
            )
            raise error

        self.report.context.iopipe.error(error)

    err = error

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(event, context):
            logger.debug("%s wrapped with IOpipe decorator" % repr(func))

            context = ContextWrapper(context, self)

            # if env var IOPIPE_ENABLED is set to False skip reporting
            if self.config["enabled"] is False:
                logger.debug("IOpipe agent disabled, skipping reporting")
                return func(event, context)

            # If a token is not present, skip reporting
            if not self.config["token"]:
                warnings.warn(
                    "Your function is decorated with iopipe, but a valid token was not "
                    "found. Set the IOPIPE_TOKEN environment variable with your IOpipe "
                    "project token."
                )
                return func(event, context)

            # If context doesn't pass validation, skip reporting
            if not self.validate_context(context):
                logger.debug("Invalid context, skipping reporting")
                return func(event, context)

            self.run_hooks("pre:invoke", event=event, context=context)

            self.report = Report(self, context)

            timeout_duration = 0

            # Disable timeout if timeout_window <= 0, or if our context doesn't have a
            # get_remaining_time_in_millis method
            if (
                self.config["timeout_window"] > 0
                and hasattr(context, "get_remaining_time_in_millis")
                and callable(context.get_remaining_time_in_millis)
            ):
                timeout_duration = (
                    context.get_remaining_time_in_millis() / 1000.0
                ) - self.config["timeout_window"]

                # The timeout_duration cannot be a negative number, disable if it is
                timeout_duration = max([0, timeout_duration])

                # Maximum execution time is 15 minutes, make sure timeout doesn't
                # exceed that minus the timeout window
                timeout_duration = min(
                    [timeout_duration, 60 * 60 * 15 - self.config["timeout_window"]]
                )

            if timeout_duration > 0:
                logger.debug("Setting timeout duration to %s" % timeout_duration)

            result = None

            try:
                with Timeout(timeout_duration, False) as timeout:
                    result = func(event, context)
            except Exception as e:

                self.run_hooks("post:invoke", event=event, context=context)

                frame = None
                if isinstance(e, TimeoutError):
                    frame = inspect.currentframe()

                # This prevents this block from being executed a second time in the
                # event that a timeout occurs and an exception is subsequently raised
                # within the handler
                if self.report.sent is False:
                    self.report.prepare(e, frame)
                    self.run_hooks("pre:report")
                    self.report.send()
                    self.run_hooks("post:report")

                raise e
            else:
                self.run_hooks("post:invoke", event=event, context=context)
                self.report.prepare()
                self.run_hooks("pre:report")
                self.report.send()
                self.run_hooks("post:report")
            finally:
                timeout.cancel()
                self.wait_for_futures()

            return result

        return wrapped

    decorator = __call__

    def load_plugins(self, plugins):
        """
        Loads plugins that match the `Plugin` interface and are instantiated.

        :param plugins: A list of plugin instances.
        """

        def instantiate(plugin):
            return plugin() if inspect.isclass(plugin) else plugin

        loaded_plugins = []
        plugins_seen = []

        # Iterate over plugins in reverse to permit users to override default
        # plugin config
        for plugin in reversed(plugins):
            if not is_plugin(plugin) or plugin.name in plugins_seen:
                continue
            # Build the plugins list in reverse to restore original order
            loaded_plugins.insert(0, instantiate(plugin))
            plugins_seen.append(plugin.name)

        return loaded_plugins

    def run_hooks(self, name, event=None, context=None):
        """
        Runs plugin hooks for each registered plugin.
        """
        hooks = {
            "pre:setup": lambda p: p.pre_setup(self),
            "post:setup": lambda p: p.post_setup(self),
            "pre:invoke": lambda p: p.pre_invoke(event, context),
            "post:invoke": lambda p: p.post_invoke(event, context),
            "pre:report": lambda p: p.pre_report(self.report),
            "post:report": lambda p: p.post_report(self.report),
        }

        if name in hooks:
            for p in self.plugins:
                if p.enabled:
                    try:
                        hooks[name](p)
                    except Exception as e:
                        logger.error(
                            "IOpipe plugin %s hook raised error" % (name, str(e))
                        )
                        logger.exception(e)

    def submit_future(self, func, *args, **kwargs):
        """
        Submit a function call to be run as a future in a thread pool. This
        should be an I/O bound operation.
        """
        # This mode will run futures synchronously. This should only be used
        # for benchmarking purposes.
        if self.config["sync_http"] is True:
            return MockFuture(func, *args, **kwargs)

        future = self.pool.submit(func, *args, **kwargs)
        self.futures.append(future)
        return future

    def wait_for_futures(self):
        """
        Wait for all futures to complete. This should be done at the end of an
        an invocation.
        """
        [future for future in futures.as_completed(self.futures)]
        self.futures = []

    def validate_context(self, context):
        """
        Checks to see if we're working with a valid lambda context object.

        :returns: True if valid, False if not
        :rtype: bool
        """
        return all(
            [
                hasattr(context, attr)
                for attr in [
                    "aws_request_id",
                    "function_name",
                    "function_version",
                    "get_remaining_time_in_millis",
                    "invoked_function_arn",
                    "log_group_name",
                    "log_stream_name",
                    "memory_limit_in_mb",
                ]
            ]
        ) and callable(context.get_remaining_time_in_millis)
