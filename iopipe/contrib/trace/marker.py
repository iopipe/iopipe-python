import functools


class Marker(object):
    def __init__(self, timeline, context):
        self.timeline = timeline
        self.context = context
        self.contexts = []

    def __call__(self, name):
        self.contexts.append(name)
        return self

    def __enter__(self):
        if self.contexts:
            self.start(self.contexts[-1])
        return self

    def __exit__(self, type, value, traceback):
        if self.contexts:
            self.end(self.contexts[-1])
            self.contexts.pop()

    def decorator(self, name):
        return MarkerDecorator(self, name)

    def start(self, name):
        self.timeline.mark("start:%s" % name)
        self.context.iopipe.label("@iopipe/plugin-trace")

    def end(self, name):
        self.timeline.mark("end:%s" % name)

    def measure(self, name, start=None, end=None):
        return self.timeline.measure(
            "measure:%s" % name,
            "start:%s" % (start or name),
            "end:%s" % (end or start or name),
        )

    def delete(self, name):
        self.timeline.delete(name)

    def db_trace(self, trace, db_type, request):
        if self.context.instance.report is None:
            return

        entry = trace._asdict()
        entry["type"] = entry.pop("entryType")
        entry["dbType"] = db_type

        if request is not None:
            entry["request"] = request

        self.context.instance.report.db_trace_entries.append(entry)

    def http_trace(self, trace, request, response):
        if self.context.instance.report is None:
            return

        entry = trace._asdict()
        entry["type"] = entry.pop("entryType")

        if request is not None:
            entry["request"] = request

        if response is not None:
            entry["response"] = response

        self.context.instance.report.http_trace_entries.append(entry)


class MarkerDecorator(object):
    def __init__(self, marker, name):
        self.marker = marker
        self.name = name

    def __call__(self, func):
        self.marker.contexts.append(self.name)

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            self.marker.start(self.marker.contexts[-1])
            return_value = func(*args, **kwargs)
            self.marker.end(self.marker.contexts[-1])
            self.marker.contexts.pop()
            return return_value

        return wrapped
