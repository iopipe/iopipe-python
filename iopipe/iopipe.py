import sys
import time
import os

from .report import Report
from .collector import get_collector_url


def get_pid_stat(pid):
    with open("/proc/%s/stat" % (pid,)) as stat_file:
        stat = stat_file.readline().split(" ")
        return {
            'utime': int(stat[13]),
            'stime': int(stat[13]),
            'cutime': int(stat[15]),
            'cstime': int(stat[16]),
            'rss': int(stat[23])
        }


class IOpipe(object):
    def __init__(self,
                 client_id=None,
                 url=get_collector_url(os.getenv('AWS_REGION')),
                 debug=False):
        self.config = {
            'url': url,
            'debug': debug,
            'client_id': client_id
        }

    def create_report(self, start_time, context):
        """
        Used in advanced usage to manually set the report start_report
        """
        self.report = Report(self.config,
                             get_pid_stat('self'))
        try:
            self.report.update_data(context, start_time)
            return self.report
        except Exception as err:
            self.report.retain_err(err)
            self.send()
            raise err

    def log(self, key, value):
        """
        Add custom data to the report
        """
        event = {
            'name': str(key)
        }

        # Add numerical values to report
        if (isinstance(value, int) or
            isinstance(value, float) or
           (isinstance(value, long) if (sys.version_info[0] < 3) else False)):
                event['n'] = value
        else:
            event['s'] = str(value)
        self.report.custom_metrics.append(event)

    def err(self, err):
        self.report.retain_err(err)
        self.send()
        raise err

    def decorator(self, fun):
        def wrapped(event, context):
            err = None
            start_time = time.time()

            self.report = self.create_report(start_time, context)
            try:
                result = fun(event, context)
            except Exception as err:
                self.report.retain_err(err)
                self.report.send()
                raise err
            finally:
                self.report.send()
            return result
        return wrapped
