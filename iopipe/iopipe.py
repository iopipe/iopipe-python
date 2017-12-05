import decimal
import functools
import logging
import numbers
import signal
import warnings

from .config import set_config
from .report import Report

logging.basicConfig()

logger = logging.getLogger('iopipe')
logger.setLevel(logging.INFO)


class IOpipe(object):
    def __init__(self, token=None, url=None, debug=None, **options):
        if token is not None:
            options['token'] = token
        if url is not None:
            options['url'] = url
        if debug is not None:
            options['debug'] = debug

        self.config = set_config(**options)
        self.report = None

        if self.config['debug']:
            logger.setLevel(logging.DEBUG)

    def log(self, key, value):
        if self.report is None:
            warnings.warn('Attempting to log metrics before function decorated with IOpipe. '
                          'This metric will not be recorded.')
            return

        event = {
            'name': str(key)
        }

        # Add numerical values to report
        # We typecast decimals as strings: not JSON serializable and casting to floats can result in rounding errors.
        if isinstance(value, numbers.Number) and not isinstance(value, decimal.Decimal):
            event['n'] = value
        else:
            event['s'] = str(value)

        self.report.custom_metrics.append(event)

    def error(self, error):
        if self.report is None:
            warnings.warn('An exception occurred before function was decorated with IOpipe. '
                          'This exception will not be recorded.')
            raise error

        self.report.send(error)
        raise error

    err = error

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(event, context):
            logger.debug('%s wrapped with IOpipe decorator' % repr(func))

            # if env var IOPIPE_ENABLED is set to False skip reporting
            if self.config['enabled'] is False:
                logger.debug('IOpipe agent disabled, skipping reporting')
                return func(event, context)

            # If a token is not present, skip reporting
            if not self.config['token']:
                warnings.warn('Your function is decorated with iopipe, but a valid token was not found. '
                              'Set the IOPIPE_TOKEN environment variable with your IOpipe project token.')
                return func(event, context)

            self.report = Report(self.config, context)

            # Partial acts as a closure here so that a reference to the report is passed to the timeout handler
            signal.signal(signal.SIGALRM, functools.partial(self.timeout_handler, self.report))

            # Disable timeout if timeout_window <= 0, or if our context doesn't have a get_remaining_time_in_millis
            if self.config['timeout_window'] > 0 and \
                    hasattr(context, 'get_remaining_time_in_millis') and \
                    callable(context.get_remaining_time_in_millis):
                timeout_duration = (context.get_remaining_time_in_millis() / 1000.0) - self.config['timeout_window']

                # The timeout_duration cannot be a negative number, disable if it is
                timeout_duration = max([0, timeout_duration])

                # Maximum execution time is 10 minutes, make sure timeout doesn't exceed that minus the timeout window
                timeout_duration = min([timeout_duration, 60 * 60 * 10 - self.config['timeout_window']])

                logger.debug('Setting timeout duration to %s' % timeout_duration)

                # Using signal.setitimer instead of signal.alarm because the latter only accepts integers and we want to
                # be able to timeout at millisecond granularity
                signal.setitimer(signal.ITIMER_REAL, timeout_duration)

            result = None

            try:
                result = func(event, context)
            except Exception as e:
                self.report.send(e)
                raise e
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                self.report.send()

            return result
        return wrapped

    decorator = __call__

    def timeout_handler(self, report, signum, frame):
        """
        Catches a timeout (SIGALRM) and sends the report before actual timeout occurs.

        The signum and frame parameters are passed by the signal module to this handler.

        :param report: The current report instance.
        :param signum: The signal number being handled.
        :param frame: The stack frame when signal was raised.
        """
        logger.debug('Function is about to timeout, sending report')
        report.send()
