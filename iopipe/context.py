import decimal
import numbers
import warnings


class ContextWrapper(object):
    def __init__(self, base_context, instance):
        self.base_context = base_context
        self.instance = instance
        self.iopipe = IOpipeContext(self.instance)

    def __getattr__(self, name):
        return getattr(self.base_context, name)


class IOpipeContext(object):
    def __init__(self, instance):
        self.instance = instance

    def log(self, key, value):
        if self.instance.report is None:
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

        self.instance.report.custom_metrics.append(event)

    def error(self, error):
        if self.instance.report is None:
            warnings.warn('An exception occurred before function was decorated with IOpipe. '
                          'This exception will not be recorded.')
            raise error

        self.instance.report.prepare(error)
        self.instance.run_hooks('pre:report')
        self.instance.report.send()
        self.instance.run_hooks('post:report')
        raise error

    def register(self, name, value):
        if not hasattr(self, name):
            setattr(self, name, value)

    def unregister(self, name):
        if hasattr(self, name):
            delattr(self, name)
