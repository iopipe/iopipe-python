class Marker(object):
    def __init__(self, timeline):
        self.timeline = timeline

    def start(self, name):
        self.timeline.mark('start:%s' % name)

    def end(self, name):
        self.timeline.mark('end:%s' % name)

    def measure(self, name, start, end):
        self.timeline.measure('measure:%s' % name, 'start:%s' % start, 'end:%s' % end)
