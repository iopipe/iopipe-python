import datetime
import json
import socket
import sys
import time

import constants

try:
    import requests
except:
    from botocore.vendored import requests


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
                 url=constants.DEFAULT_ENDPOINT_URL,
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
            "events": {}
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

    def _add_python_local_data(self, get_all=False):
        """
        Add the python sys attributes relevant to AWS Lambda execution
        """
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
        if key in self.report['events']:
            # the key exists, merge the data
            if isinstance(self.report['events'][key], list):
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
            'time_reported': datetime.datetime.now()
            .strftime(constants.TIMESTAMP_FORMAT)
        }
        if 'errors' not in self.report:
            self.report['errors'] = err_details
        elif not isinstance(self.report['errors'], list):
            self.report['errors'] = [self.report['errors']]
        else:
            self.report['errors'].append(err_details)

        # add the full local python data as well
        self._add_python_local_data(get_all=True)

    def send(self, context=None, time_start=None):
        """
        Send the current report to IOpipe
        """
        json_report = None

        self._add_pid_data('self')

        # Duration of execution.
        duration = time.time() - (time_start or time.time())
        self.report.update({
            'duration': int(duration * 1000000000),
            'time_sec': int(duration),
            'time_nanosec': int((duration - int(duration)) * 1000000000)
        })

        self.report['environment'].update(
            {
                'agent': {
                  'runtime': "python",
                  'version': constants.VERSION
                }
            })

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
        except Exception as err:
            print('Error reporting metrics to IOpipe. {}'.format(err))
        finally:
            if self._debug:
                print(json_report)
            # Clear events between invocations!
            self.report['events'] = {}

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
