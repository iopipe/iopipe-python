import time
import platform
import traceback
import datetime
import socket
import json

from . import constants

try:
    import requests
except:
    from botocore.vendored import requests

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


class Report(object):
    """
    The report of system status
    """
    def __init__(self, config, stat_start):
        self.client_id = config['client_id']
        self._debug = config['debug']
        self._url = config['url']
        self.environment = {
            'agent': {
                'runtime': "python",
                'version': constants.VERSION,
                'load_time': constants.MODULE_LOAD_TIME
            },
            'host': {},
            'os': {
                'cpus': [],
                'linux': {
                    'mem': {},
                    'pid': {
                        'self': {
                            'stat_start': stat_start
                        },
                    }
                }
            },
            'python': {
                'version': platform.python_version()
            }
        }
        self.custom_metrics = []

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
                # First cpu line is aggregation of following lines, skip it
                if len(cpu_stat[0]) == 3:
                    continue
                self.environment['os']['cpus'].append({
                    'name': cpu_stat[0],
                    'times': {
                        'user': cpu_stat[1],
                        'nice': cpu_stat[2],
                        'sys': cpu_stat[3],
                        'idle': cpu_stat[4],
                        'irq': cpu_stat[6]
                    }
                })

        with open("/proc/uptime") as uptime_file:
            utf = uptime_file.readline().split(" ")
            uptime = int(float(utf[0]))

        with open("/proc/sys/kernel/random/boot_id") as bootid_file:
            self.environment['host'].update({
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
            self.environment['os']['linux']['mem'].update(linux_mem)

        self.environment['os'].update({
            'hostname': socket.gethostname(),
            'uptime': uptime,
            'freemem':
                self.environment['os']['linux']['mem']['MemFree'],
            'totalmem':
                self.environment['os']['linux']['mem']['MemTotal'],
            'usedmem':
                self.environment['os']['linux']['mem']['MemTotal'] -
                self.environment['os']['linux']['mem']['MemFree']
        })

    def _add_pid_data(self, pid):
        self.environment['os']['linux']['pid'][pid] = \
            self.environment['os']['linux']['pid'][pid] or {}

        self.environment['os']['linux']['pid'][pid]['stat'] = \
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
            self.environment['os']['linux']['pid'][pid]['status'] \
                = status

    def _add_aws_lambda_data(self, context):
        """
        Add AWS Lambda specific data to the report
        """
        self.aws = {}

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
                self.aws[k] = getattr(context, v)

        if context and 'get_remaining_time_in_millis' in dir(context):
            try:
                self.aws['getRemainingTimeInMillis'] = \
                    context.get_remaining_time_in_millis()
            except Exception:
                pass  # @TODO handle this more gracefully

    def update_data(self, context, start_time):
        self._add_pid_data('self')

        # Duration of execution.
        duration = time.time() - (start_time or time.time())
        self.duration = int(duration * 1000000000)
        self.time_sec = int(duration)
        self.time_nanosec = int((duration - int(duration)) * 1000000000),
        self.coldstart = constants.COLDSTART
        constants.COLDSTART = False

        if context:
            self._add_aws_lambda_data(context)
        self._add_os_host_data()

    def retain_err(self, err):
        """
        Add the details of an error to the report
        """
        err_details = {
            'name': type(err).__name__,
            'message': '{}'.format(err),
            'stack': traceback.format_exc(),
            'time_reported': datetime.datetime.now()
            .strftime(constants.TIMESTAMP_FORMAT)
        }
        self.errors = err_details

    def send(self):
        """
        Send the current report to IOpipe
        """
        json_report = None

        try:
            json_report = json.dumps(self, default=lambda o: o.__dict__)
        except Exception as err:
            print("Could not convert the report to JSON. "
                  "Threw exception: {}".format(err))
            print('Report: {}'.format(self))
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
