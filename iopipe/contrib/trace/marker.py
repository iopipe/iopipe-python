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

    def http_trace(self, trace, request, response):
        if self.context.instance.report is None:
            return

        entry = trace._asdict()
        entry["type"] = entry.pop("entryType")
        if request is not None:
            entry["request"] = request._asdict()
        if response is not None:
            entry["response"] = response._asdict()

        self.context.instance.report.http_trace_entries.append(entry)
