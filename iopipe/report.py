import datetime
import json
import logging
import platform
import sys
import time
import traceback

from . import constants
from .monotonic import monotonic
from .send_report import send_report

if sys.platform.startswith('linux'):
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
        Instantiates a new IOpipe report.

        :param config: The IOpipe agent config.
        :param context: The AWS Lambda context.
        """
        self.sent = False
        self.start_time = monotonic()
        self.stat_start = system.read_pid_stat('self')

        self.config = config
        self.context = context
        self.custom_metrics = []
        self.plugins = config['plugins']

        self.report = {
            'client_id': self.config['token'],
            'coldstart': constants.COLDSTART,
            'custom_metrics': self.custom_metrics,
            'environment': {
                'agent': {
                    'load_time': constants.MODULE_LOAD_TIME,
                    'runtime': 'python',
                    'version': constants.VERSION,
                },
                'python': {
                    'version': platform.python_version(),
                },
                'host': {},
                'os': {
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

        duration = monotonic() - self.start_time

        self.report['environment']['host']['boot_id'] = system.read_bootid()

        self.report['environment']['os']['linux']['mem'] = meminfo = system.read_meminfo()

        self.report.update({
            'aws': self.extract_context_data(),
            'duration': int(duration * 1e9),
            'time_sec': int(duration),
            'time_nanosec': int((duration - int(duration)) * 1e9),
            'timestamp': int(time.time() * 1000),
        })

        self.report['environment']['os'].update({
            'arch': system.read_arch(),
            'cpus': system.read_stat(),
            'freemem': meminfo['MemFree'],
            'hostname': system.read_hostname(),
            'totalmem': meminfo['MemTotal'],
            'uptime': system.read_uptime(),
            'usedmem': meminfo['MemTotal'] - meminfo['MemFree'],
        })

        self.report['environment']['os']['linux']['pid'] = {
            'self': {
                'stat': system.read_pid_stat('self'),
                'stat_start': self.stat_start,
                'status': system.read_pid_status('self'),
            },
        }

        logger.debug('Sending report to IOpipe:')
        logger.debug(json.dumps(self.report, indent=2, sort_keys=True))

        send_report(self.report, self.config)
