class Marker(object):
    def __init__(self, timeline):
        self.timeline = timeline

    def start(self, name):
        self.timeline.mark('start:%s' % name)

    def end(self, name):
        self.timeline.mark('end:%s' % name)

    def measure(self, name, start=None, end=None):
        self.timeline.measure(
            'measure:%s' % name,
            'start:%s' % (start or name),
            'end:%s' % (end or start or name))
