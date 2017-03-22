import json
import time
import os

from report import Report
from collector import get_collector_url

try:
    import requests
except:
    from botocore.vendored import requests


MODULE_LOAD_TIME = time.time() * 1000
COLDSTART = True
REQUESTS_SESSION = requests.Session()


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
        self._url = url
        self._debug = debug
        self.client_id = client_id

    def start_report(self, start_time, context):
        """
        Used in advanced usage to manually set the report start_report
        """
        global COLDSTART
        self.report = Report(self.client_id, get_pid_stat('self'), MODULE_LOAD_TIME)
        try:
            self.report.update_data(context, COLDSTART, start_time)
            COLDSTART = False
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
                isinstance(value, long)):
            event['n'] = value
        else:
            event['s'] = str(value)
        self.report.custom_metrics.append(event)

    def err(self, err):
        self.report.retain_err(err)
        self.send()
        raise err

    def send(self):
        """
        Send the current report to IOpipe
        """
        json_report = None

        try:
            json_report = json.dumps(self.report, default=lambda o: o.__dict__)
        except Exception as err:
            print("Could not convert the report to JSON. "
                  "Threw exception: {}".format(err))
            print('Report: {}'.format(self.report))
            return

        try:
            response = REQUESTS_SESSION.post(
                self._url + '/v0/event',
                data=json_report,
                headers={"Content-Type": "application/json"})
            if self._debug:
                print('POST response: {}'.format(response))
        except Exception as err:
            print('Error reporting metrics to IOpipe. {}'.format(err))
        finally:
            if self._debug:
                print(json_report)

    def decorator(self, fun):
        def wrapped(event, context):
            err = None
            start_time = time.time()
            self.start_report(start_time, context)
            try:
                result = fun(event, context)
            except Exception as err:
                self.report.retain_err(err)
                self.send()
                raise err
            finally:
                self.send()
            return result
        return wrapped
