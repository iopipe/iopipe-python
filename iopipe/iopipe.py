import decimal
import numbers
import warnings

import monotonic

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

    def create_report(self, start_time, context):
        """
        Used in advanced usage to manually set the report start_report
        """
        self.report = Report(self.config)
        return self.report

    def log(self, key, value):
        """
        Add custom data to the report
        """
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

    def err(self, err):
        self.report.retain_err(err)
        self.report.send()
        raise err

    def decorator(self, fun):
        def wrapped(event, context):
            # if env var IOPIPE_ENABLED is set to False skip reporting
            if self.config['enabled'] is False:
                return fun(event, context)

            if not self.config['client_id']:
                warnings.warn('Your function is decorated with iopipe, but a valid token was not found.')

            err = None
            start_time = monotonic.monotonic()
            self.create_report(start_time, context)

            try:
                result = fun(event, context)
            except Exception as err:
                self.report.retain_err(err)
                raise err
            finally:
                try:
                    self.report.update_data(context, start_time)
                except Exception as err:
                    self.report.retain_err(err)
                    raise err
                finally:
                    self.report.send()
            return result
        return wrapped
