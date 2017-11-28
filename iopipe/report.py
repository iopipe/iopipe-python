import datetime
import logging
import platform
import sys
import time
import traceback

import monotonic

from . import constants
from .send_report import send_report

if sys.platform == 'linux2':
    from . import system
else:
    from . import mock_system as system

logger = logging.getLogger(__name__)


class Report(object):
    """
    The report of system status
    """

    def __init__(self, config, context):
        """
        Instantiates a new report.

        :param config: The IOpipe agent config.
        :param context: The AWS Lambda context.
        """
        self.sent = False
        self.start_time = monotonic.monotonic()
        self.stat_start = system.read_pid_stat('self')

        self.config = config
        self.context = context
        self.custom_metrics = []
        self.debug = config.get('debug', False)
        self.plugins = config.get('plugins', [])

        self.report = {
            'aws': {},
            'client_id': self.config.get('client_id'),
            'coldstart': constants.COLDSTART,
            'custom_metrics': self.custom_metrics,
            'duration': None,
            'environment': {
                'agent': {
                    'runtime': 'python',
                    'version': constants.VERSION,
                    'load_time': constants.MODULE_LOAD_TIME,
                },
                'python': {
                    'version': platform.python_version(),
                    'memoryUsage': None,
                },
                'host': {
                    'container_id': None,
                },
                'os': {
                    'arch': system.read_arch(),
                    'cpus': [],
                    'linux': {},
                },
            },
            'errors': {},
            'installMethod': self.config.get('install_method'),
            'plugins': self.plugins,
            'processId': constants.PROCESS_ID,
        }

        constants.COLDSTART = False

    def extract_context_data(self):
        """
        Returns the contents of a AWS Lambda context.

        :returns: A dict of relevant context data.
        :rtype: dict
        """
        data = {}
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
            if hasattr(self.context, v):
                data[k] = getattr(self.context, v)
        if hasattr(self.context, 'get_remaining_time_in_millis') and \
                callable(self.context.get_remaining_time_in_millis):
            data['getRemainingTimeInMillis'] = self.context.get_remaining_time_in_millis()
        return data

    def retain_error(self, error):
        """
        Adds details of an error to the report.

        :param error: The error exception to add to the report.
        """
        details = {
            'name': type(error).__name__,
            'message': '{}'.format(error),
            'stack': traceback.format_exc(),
            'time_reported': datetime.datetime.now().strftime(constants.TIMESTAMP_FORMAT),
        }
        self.report['errors'] = details

    def send(self, error=None):
        """
        Send the current report to IOpipe.

        :param error: An optional error to add to report.
        """
        if self.sent:
            return
        self.sent = True

        if error:
            self.retain_error(error)

        duration = monotonic.monotonic() - self.start_time

        self.report['environment']['host']['boot_id'] = \
            self.report['environment']['host']['container_id'] = \
            system.read_bootid()

        self.report['environment']['os']['linux']['mem'] = meminfo = system.read_meminfo()

        self.report.update({
            'aws': self.extract_context_data(),
            'duration': int(duration * 1e9),
            'environment': {
                'os': {
                    'cpus': system.read_stat(),
                    'freemem': meminfo['MemFree'],
                    'hostname': system.read_hostname(),
                    'linux': {
                        'pid': {
                            'self': {
                                'stat': system.read_pid_stat('self'),
                                'stat_start': self.stat_start,
                                'status': system.read_pid_status('self'),
                            },
                        },
                    },
                    'totalmem': meminfo['MemTotal'],
                    'uptime': system.read_uptime(),
                    'usedmem': meminfo['MemTotal'] - meminfo['MemFree'],
                },
            },
            'time_sec': int(duration),
            'time_nanosec': int((duration - int(duration)) * 1e9),
            'timestamp': int(time.time() * 1000),
        })

        send_report(self.report, self.config)
