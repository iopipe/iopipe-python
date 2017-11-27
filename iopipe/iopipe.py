import decimal
import functools
import numbers
import warnings

from .config import set_config
from .report import Report


class IOpipe(object):
    def __init__(self, client_id=None, url=None, debug=None, **options):
        if client_id is not None:
            options['client_id'] = client_id
        if url is not None:
            options['url'] = url
        if debug is not None:
            options['debug'] = debug
        self.config = set_config(**options)
        self.report = None

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
                          'This exceptionwill not be recorded.')
            raise error

        self.report.send(error)
        raise error

    err = error

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(event, context):
            # if env var IOPIPE_ENABLED is set to False skip reporting
            if self.config['enabled'] is False:
                return func(event, context)

            # If a token is not present, skip reporting
            if not self.config['client_id']:
                warnings.warn('Your function is decorated with iopipe, but a valid token was not found. '
                              'Set the IOPIPE_TOKEN environment variable with your IOpipe token.')
                return func(event, context)

            self.report = Report(self.config, context)

            try:
                result = func(event, context)
            except Exception as e:
                self.report.send(e)
                raise e
            finally:
                self.report.send()
            return result
        return wrapped

    decorator = __call__
