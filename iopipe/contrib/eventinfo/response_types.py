from .util import get_value


class ResponseType(object):
    keys = []

    def __init__(self, event_type):
        self.event_type = event_type

    def collect(self, response):
        response_info = {}

        for key in self.keys:
            if isinstance(key, tuple):
                old_key, new_key = key
            else:
                old_key = new_key = key
            value = get_value(response, old_key)
            if value is not None:
                response_info[
                    "@iopipe/event-info.%s.response.%s" % (self.event_type, new_key)
                ] = value

        return response_info


class LambdaProxy(ResponseType):
    keys = ["statusCode"]
