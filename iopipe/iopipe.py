import datetime
import json
import platform
import socket
import time
import os

import constants
from collector import get_collector_url

try:
    import requests
except:
    from botocore.vendored import requests


MODULE_LOAD_TIME = time.time() * 1000
COLDSTART = True


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
        self.report = {
            'client_id': self.client_id,
            'environment': {
                'host': {},
                'os': {
                    'linux': {
                        'cpu': {},
                        'mem': {},
                        'pid': {
                            'self': {}
                        }
                    }
                },
                'python': {}
            },
            "custom_metrics": []
        }

        self.report['environment']['os']['linux']['pid'].update({
            'self': {
                'stat_start': get_pid_stat('self')
            }
        })

    def __del__(self):
        """
        Send the report if it hasn't already been sent
        """
        self.send()

    def _add_aws_lambda_data(self, context):
        """
        Add AWS Lambda specific data to the report
        """
        aws_key = 'aws'
        self.report[aws_key] = {}

        for k, v in {
            # camel case names in the report to align with AWS standards
            'functionName': 'function_name',
            'functionVersion': 'function_version',
            'memoryLimitInMB': 'memory_limit_in_mb',
            'invokedFunctionArn': 'invoked_function_arn',
            'awsRequestId': 'aws_request_id',
            'logGroupName': 'log_group_name',
            'logStreamName': 'log_stream_name',
        }.items():
            if v in dir(context):
                self.report[aws_key][k] = getattr(context, v)

        if context and 'get_remaining_time_in_millis' in dir(context):
            try:
                self.report['aws']['getRemainingTimeInMillis'] = \
                    context.get_remaining_time_in_millis()
            except Exception:
                pass  # @TODO handle this more gracefully

    def _add_pid_data(self, pid):
        self.report['environment']['os']['linux']['pid'][pid] = \
            self.report['environment']['os']['linux']['pid'][pid] or {}

        self.report['environment']['os']['linux']['pid'][pid]['stat'] = \
            get_pid_stat(pid)

        with open("/proc/%s/status" % (pid,)) as status_file:
            status = {}
            for row in status_file:
                line = row.split(":")
                status_value = line[1].rstrip("\t\n kB").lstrip()
                try:
                    status[line[0]] = int(status_value)
                except ValueError:
                    status[line[0]] = status_value
            self.report['environment']['os']['linux']['pid'][pid]['status'] \
                = status

    def _add_os_host_data(self):
        """
        Add os field to payload
        """
        uptime = None

        with open("/proc/stat") as stat_file:
            for line in stat_file:
                cpu_stat = line.split(" ")
                if cpu_stat[0][:3] != "cpu":
                    break
                self.report['environment']['os']['linux']['cpu'][cpu_stat[0]] \
                    = {
                        'user': cpu_stat[1],
                        'nice': cpu_stat[2],
                        'system': cpu_stat[3],
                        'idle': cpu_stat[4],
                        'iowait': cpu_stat[5],
                        'irq': cpu_stat[6],
                        'softirq': cpu_stat[7]
                }

        with open("/proc/uptime") as uptime_file:
            utf = uptime_file.readline().split(" ")
            uptime = int(float(utf[0]))

        with open("/proc/sys/kernel/random/boot_id") as bootid_file:
            self.report['environment']['host'].update({
                'container_id': bootid_file.readline()
            })

        with open("/proc/meminfo") as meminfo:
            linux_mem = {}
            for row in meminfo:
                line = row.split(":")
                # Example content:
                # MemTotal:                3801016 kB
                # MemFree:                 1840972 kB
                # MemAvailable:        3287752 kB
                # HugePages_Total:             0
                linux_mem[line[0]] = \
                    int(line[1].lstrip().rstrip(" kB\n"))
            self.report['environment']['os']['linux']['mem'].update(linux_mem)

        self.report['environment']['os'].update({
            'hostname': socket.gethostname(),
            'uptime': uptime,
            'freemem':
                self.report['environment']['os']['linux']['mem']['MemFree'],
            'totalmem':
                self.report['environment']['os']['linux']['mem']['MemTotal'],
            'usedmem':
                self.report['environment']['os']['linux']['mem']['MemTotal'] -
                self.report['environment']['os']['linux']['mem']['MemFree']
        })

    def _add_python_local_data(self):
        """
        Add the python sys attributes relevant to AWS Lambda execution
        """
        self.report['environment']['python']['version'] = \
            platform.python_version()

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
        self.report['custom_metrics'].append(event)

    def err(self, err):
        """
        Add the details of an error to the report
        """
        err_details = {
            'exception': '{}'.format(err),
            'time_reported': datetime.datetime.now()
            .strftime(constants.TIMESTAMP_FORMAT)
        }
        if 'errors' not in self.report:
            self.report['errors'] = err_details
        elif not isinstance(self.report['errors'], list):
            self.report['errors'] = [self.report['errors']]
        else:
            self.report['errors'].append(err_details)

        self._add_python_local_data()

    def send(self, context=None, time_start=None):
        """
        Send the current report to IOpipe
        """
        global COLDSTART
        json_report = None

        self._add_pid_data('self')

        # Duration of execution.
        duration = time.time() - (time_start or time.time())
        self.report.update({
            'duration': int(duration * 1000000000),
            'time_sec': int(duration),
            'time_nanosec': int((duration - int(duration)) * 1000000000),
            'coldstart': COLDSTART
        })

        if COLDSTART:
            COLDSTART = False

        self.report['environment'].update(
            {
                'agent': {
                  'runtime': "python",
                  'version': constants.VERSION,
                  'load_time': MODULE_LOAD_TIME
                }
            })

        if context:
            self._add_aws_lambda_data(context)
        self._add_python_local_data()
        self._add_os_host_data()

        try:
            json_report = json.dumps(self.report)
        except Exception as err:
            print("Could not convert the report to JSON."
                  "Threw exception: {}".format(err))
            print('Report: {}'.format(self.report))
            return

        try:
            response = requests.post(
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
            # Clear custom metrics between invocations!
            self.report['custom_metrics'] = []

    def decorator(self, fun):
        def wrapped(event, context):
            err = None
            start_time = time.time()
            try:
                result = fun(event, context)
            except Exception as err:
                self.err(err)
                raise err
            finally:
                self.send(context, start_time)
            return result
        return wrapped
