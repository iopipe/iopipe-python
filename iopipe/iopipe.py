import datetime
import json
import os
import socket
import sys
import time

try:
  import requests
except:
  from botocore.vendored import requests

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DEFAULT_ENDPOINT_URL = "https://metrics-api.iopipe.com"
VERSION = "0.1.3"


class IOpipe(object):
    def __init__(self,
                 client_id=None,
                 url=DEFAULT_ENDPOINT_URL,
                 debug=False):
        self._url = url
        self._debug = debug
        self._time_start = time.time()
        self.client_id = client_id
        self.report = {
            'client_id': self.client_id,
            }
        self._sent = False

    def __del__(self):
        """
        Send the report if it hasn't already been sent
        """
        if not self._sent:
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
            except Exception as aws_lambda_err:
                pass  # @TODO handle this more gracefully

    def _add_os_host_data(self):
        """
        Add os field to payload
        """
        uptime = None
        self.report['environment']['os'] = self.report.get('os', {})
        self.report['environment']['os']['linux'] = \
            self.report['environment']['os'].get('linux', {})
        self.report['environment']['os']['linux']['mem'] = \
            self.report['environment']['os']['linux'].get('mem', {})

        with open("/proc/stat") as stat_file:
            self.report['environment']['os']['linux']['cpu'] = {}
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

        with open("/proc/loadavg") as loadavg_file:
            loadavg = loadavg_file.readline().split(" ")
            self.report['environment']['os']['linux']['loadavg'] = {
                loadavg[0],
                loadavg[1],
                loadavg[2]
            }

        with open("/proc/uptime") as uptime_file:
            utf = uptime_file.readline().split(" ")
            uptime = int(float(utf[0]))

        with open("/proc/sys/kernel/random/boot_id") as bootid_file:
            self.report['environment']['host']['container_id'] = \
                bootid_file.readline()

        with open("/proc/meminfo") as meminfo:
            for row in meminfo:
                line = row.split(":")
                # Example content:
                # MemTotal:                3801016 kB
                # MemFree:                 1840972 kB
                # MemAvailable:        3287752 kB
                # HugePages_Total:             0
                self.report['environment']['os']['linux']['mem'][line[0]] = \
                    int(line[1].lstrip().rstrip(" kB\n"))

        self.report['environment']['os'] = {
            'hostname': socket.gethostname(),
            'uptime': uptime,
            'freemem':
                self.report['environment']['os']['linux']['mem']['MemFree'],
            'totalmem':
                self.report['environment']['os']['linux']['mem']['MemTotal'],
            'usedmem':
                self.report['environment']['os']['linux']['mem']['MemTotal'] -
                self.report['environment']['os']['linux']['mem']['MemFree']
        }

    def _add_python_local_data(self, get_all=False):
        """
        Add the python sys attributes relevant to AWS Lambda execution
        """
        self.report['environment'] = {}
        self.report['environment']['python'] = {}

        sys_attr = {}
        if get_all:  # full set of data
            sys_attr = {
                # lower_ case to align with python standards
                'argv': 'argv',
                'byte_order': 'byteorder',
                'builtin_module_names': 'builtin_module_names',
                'executable': 'executable',
                'flags': 'flags',
                'float_info': 'float_info',
                'float_repr_style': 'float_repr_style',
                'hex_version': 'hexversion',
                'long_info': 'long_info',
                'max_int': 'maxint',
                'max_size': 'maxsize',
                'max_unicode': 'maxunicode',
                'meta_path': 'meta_path',
                'path': 'path',
                'platform': 'platform',
                'prefix': 'prefix',
                'traceback_limit': 'tracebacklimit',
                'version': 'version',
                'api_version': 'api_version',
                'version_info': 'version_info',
            }
        else:  # reduced set of data for common cases
            sys_attr = {
                # lower_ case to align with python standards
                'argv': 'argv',
                'path': 'path',
                'platform': 'platform',
                'version': 'version',
                'api_version': 'api_version',
            }

        # get the sys attributes first
        for k, v in sys_attr.items():
            if v in dir(sys):
                self.report['environment']['python']["sys_"+k] = \
                    "{}".format(getattr(sys, v))

        # now the sys functions
        if get_all:
            for k, v in {
                # lower_ case to align with python standards
                'check_interval': 'getcheckinterval',
                'default_encoding': 'getdefaultencoding',
                'dl_open_flags': 'getdlopenflags',
                'file_system_encoding': 'getfilesystemencoding',
            }.items():
                if v in dir(sys):
                    self.report['environment']['python']['sys_'+k] = \
                        "{}".format(getattr(sys, v)())

    def log(self, key, value):
        """
        Add custom data to the report
        """
        # make sure the namespace exists
        if 'events' not in self.report:
            self.report['events'] = {}

        if key in self.report['events']:
            # the key exists, merge the data
            if isinstance(self.report['events'][key], []):
                self.report['events'][key].append(value)
            else:
                self.report['events'][key] = \
                    [self.report['events'][key], value]
        else:
            self.report['events'][key] = value

    def err(self, err):
        """
        Add the details of an error to the report
        """
        err_details = {
            'exception': '{}'.format(err),
            'time_reported': datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
        }
        if 'errors' not in self.report:
            self.report['errors'] = err_details
        elif not isinstance(self.report['errors'], []):
            self.report['errors'] = [self.report['errors']]
        else:
            self.report['errors'].append(err_details)

        # add the full local python data as well
        self._add_python_local_data(get_all=True)

    def send(self, context=None):
        """
        Send the current report to IOpipe
        """
        json_report = None

        # Duration of execution.
        self.report['time_nanosec'] = \
            int((time.time() - self._time_start) * 1000000000)

        self.report['environment']['agent'] = {
            'runtime': "python",
            'version': VERSION
        }

        if context:
            self._add_aws_lambda_data(context)
        self._add_python_local_data()
        self._add_os_host_data()

        try:
            json_report = json.dumps(self.report, indent=2)
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
            self._sent = True
        except Exception as err:
            print('Error reporting metrics to IOpipe. {}'.format(err))
        finally:
            if self._debug:
                print(json_report)

    def decorator(self, fun):
        def wrapped(event, context):
            err = None
            try:
                result = fun(event, context)
            except Exception as err:
                self.err(err)
                self.send(context)
                raise err
            self.send(context)
            return result
        return wrapped
