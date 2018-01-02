class Marker(object):
    def __init__(self, timeline):
        self.timeline = timeline
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
        self.timeline.mark('start:%s' % name)

    def end(self, name):
        self.timeline.mark('end:%s' % name)

    def measure(self, name, start=None, end=None):
        self.timeline.measure(
            'measure:%s' % name,
            'start:%s' % (start or name),
            'end:%s' % (end or start or name))
