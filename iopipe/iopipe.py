import functools
import inspect
import logging
import signal
import warnings

from .config import set_config
from .context import ContextWrapper
from .plugins import is_plugin
from .report import Report

logging.basicConfig()

logger = logging.getLogger('iopipe')
logger.setLevel(logging.INFO)


class TimeoutError(Exception):
    pass


class IOpipe(object):
    def __init__(self, token=None, url=None, debug=None, plugins=None, **options):
        self.plugins = []
        if plugins is not None:
            self.plugins = self.load_plugins(plugins)
            options['plugins'] = self.plugins

        self.run_hooks('pre:setup')

        if token is not None:
            options['token'] = token
        if url is not None:
            options['url'] = url
        if debug is not None:
            options['debug'] = debug

        self.config = set_config(**options)
        self.config['plugins'] = self.load_plugins(self.config['plugins'])
        self.report = None

        if self.config['debug']:
            logger.setLevel(logging.DEBUG)

        self.run_hooks('post:setup')

    def log(self, key, value):
        if self.report is None:
            warnings.warn(
                'Attempting to log metrics before function decorated with IOpipe. '
                'This metric will not be recorded.')
            return

        self.report.context.iopipe.log(key, value)

    def error(self, error):
        if self.report is None:
            warnings.warn(
                'An exception occurred before function was decorated with IOpipe. '
                'This exception will not be recorded.')
            raise error

        self.report.context.iopipe.error(error)

    err = error

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(event, context):
            logger.debug('%s wrapped with IOpipe decorator' % repr(func))

            context = ContextWrapper(context, self)

            self.run_hooks('pre:invoke', event=event, context=context)

            # if env var IOPIPE_ENABLED is set to False skip reporting
            if self.config['enabled'] is False:
                logger.debug('IOpipe agent disabled, skipping reporting')
                return func(event, context)

            # If a token is not present, skip reporting
            if not self.config['token']:
                warnings.warn(
                    'Your function is decorated with iopipe, but a valid token was not found. '
                    'Set the IOPIPE_TOKEN environment variable with your IOpipe project token.'
                )
                return func(event, context)

            self.report = Report(self.config, context)

            signal.signal(signal.SIGALRM, self.handle_timeout)

            # Disable timeout if timeout_window <= 0, or if our context doesn't have a get_remaining_time_in_millis
            if self.config['timeout_window'] > 0 and \
                    hasattr(context, 'get_remaining_time_in_millis') and \
                    callable(context.get_remaining_time_in_millis):
                timeout_duration = (context.get_remaining_time_in_millis() /
                                    1000.0) - self.config['timeout_window']

                # The timeout_duration cannot be a negative number, disable if it is
                timeout_duration = max([0, timeout_duration])

                # Maximum execution time is 10 minutes, make sure timeout doesn't exceed that minus the timeout window
                timeout_duration = min([
                    timeout_duration,
                    60 * 60 * 10 - self.config['timeout_window']
                ])

                logger.debug(
                    'Setting timeout duration to %s' % timeout_duration)

                # Using signal.setitimer instead of signal.alarm because the latter only accepts integers and we want to
                # be able to timeout at millisecond granularity
                signal.setitimer(signal.ITIMER_REAL, timeout_duration)

            result = None

            try:
                result = func(event, context)
            except Exception as e:
                self.run_hooks('post:invoke', event=event, context=context)

                # This prevents this block from being executed a second time in the event that a timeout occurs and an
                # exception is subsequently raised within the handler
                if self.report.sent is False:
                    self.report.prepare(e)
                    self.run_hooks('pre:report')
                    self.report.send()
                    self.run_hooks('post:report')

                raise e
            else:
                self.run_hooks('post:invoke', event=event, context=context)
                self.report.prepare()
                self.run_hooks('pre:report')
                self.report.send()
                self.run_hooks('post:report')
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)

            return result

        return wrapped

    decorator = __call__

    def handle_timeout(self, signum, frame):
        """
        Catches a timeout (SIGALRM) and sends the report before actual timeout occurs.

        The signum and frame parameters are passed by the signal module to this handler.

        :param signum: The signal number being handled.
        :param frame: The stack frame when signal was raised.
        """
        logger.debug('Function is about to timeout, sending report')
        self.report.prepare(TimeoutError('Timeout Exceeded.'), frame)
        self.run_hooks('pre:report')
        self.report.send()
        self.run_hooks('post:report')

    def load_plugins(self, plugins):
        """
        Loads plugins that match the `Plugin` interface and are instantiated.

        :param plugins: A list of plugin instances.
        """

        def instantiate(plugin):
            return plugin() if inspect.isclass(plugin) else plugin

        return [instantiate(p) for p in plugins if is_plugin(p)]

    def run_hooks(self, name, event=None, context=None):
        """
        Runs plugin hooks for each registered plugin.
        """
        hooks = {
            'pre:setup': lambda p: p.pre_setup(self),
            'post:setup': lambda p: p.post_setup(self),
            'pre:invoke': lambda p: p.pre_invoke(event, context),
            'post:invoke': lambda p: p.post_invoke(event, context),
            'pre:report': lambda p: p.pre_report(self.report),
            'post:report': lambda p: p.post_report(self.report),
        }

        if name in hooks:
            [hooks[name](p) for p in self.plugins if p.enabled]
