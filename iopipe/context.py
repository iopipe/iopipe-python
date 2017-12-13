import decimal
import numbers


class Context(object):
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
        self.instance.report.send(error)
        raise error

    def register(self, name, value):
        if not hasattr(self, name):
            setattr(self, name, value)

    def unregister(self, name):
        if hasattr(self, name):
            delattr(self, name)
