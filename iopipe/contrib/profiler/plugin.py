import io
try:
   import cProfile as profile
except ImportError:
   import profile
import pstats

from iopipe.plugins import Plugin

from .request import get_signed_request, upload_profiler_report


class ProfilerPlugin(Plugin):
   name = 'profiler'
   version = '0.1.0'
   homepage = 'https://github.com/iopipe/iopipe-python'

   def __init__(self, enabled=False, sort_by='cumulative'):
      self._enabled = enabled
      self.sort_by = sort_by

   @property
   def enabled(self):
      return self._enabled

   def pre_setup(self, iopipe):
      pass

   def post_setup(self, iopipe):
      pass

   def pre_invoke(self, event, context):
      self.profile = None

      if self.enabled:
         self.profile = profile.Profile()
         self.profile.enable()

   def post_invoke(self, event, context):
      if self.profile is not None:
         self.profile.disable()

   def pre_report(self, report):
      pass

   def post_report(self, report):
      if self.profile is not None:
         stream = io.StringIO()
         pstats.Stats(self.profile, stream=stream).sort_stats(self.sort_by)
         signed_url = get_signed_request(report)
         upload_profiler_report(signed_url, stream)
         self.profile = None
