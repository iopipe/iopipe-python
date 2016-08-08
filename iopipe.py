# standard library
import datetime
import json
import sys

# 3rd party libraries
import libs.requests as requests

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

class Report(object):
  def __init__(self, client_id, lambda_context=None, custom_data_namespace='custom_data'):
    self.client_id = client_id
    self.custom_data_namespace = custom_data_namespace
    self.report = {
      'client_id': self.client_id,
      }
    if lambda_context:
      self._lambda_context = lambda_context
      self._add_aws_lambda_data()
    self._add_python_sys_data()
    self._sent = False

  def __del__(self):
    """
    Send the report if it hasn't already been sent
    """
    if not self._sent: self.send()

  def _add_aws_lambda_data(self):
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
      if v in dir(self._lambda_context):
        self.report[aws_key][k] = getattr(self._lambda_context, v)

  def _add_python_sys_data(self):
    """
    Add the python sys attributes relevant to AWS Lambda execution
    """
    python_key = 'python'
    sys_key = 'sys'
    self.report[python_key] = {}
    self.report[python_key][sys_key] = {}

    # get the sys attributes first
    for k, v in {
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
      'modules': 'modules',
    }.items():
      if v in dir(sys):
        self.report[python_key][sys_key][k] = "{}".format(getattr(sys, v))
 
    # now the sys functions
    for k, v in {
      # lower_ case to align with python standards
      'check_interval': 'getcheckinterval',
      'default_encoding': 'getdefaultencoding',
      'dl_open_flags': 'getdlopenflags',
      'file_system_encoding': 'getfilesystemencoding',
    }.items():
      if v in dir(sys):
        self.report[python_key][sys_key][k] = "{}".format(getattr(sys, v)())

  def add_custom_data(self, key, value, namespace=None):
    """
    Add custom data to the report
    """
    # make sure we have a namespace
    if not namespace: namespace = self.custom_data_namespace
    
    # make sure the namespace exists
    if not self.report.has_key(namespace): self.report[namespace] = {}
    

    if self.report[namespace].has_key(key):
      # the key exists, merge the data
      if type(self.report[namespace][key]) == type([]):
        self.report[namespace][key].append(value)
      else:
        self.report[namespace][key] = [ self.report[namespace][key], value ]
    else:
      self.report[namespace][key] = value

  def report_err(self, err):
    """
    Add the details of an error to the report
    """
    err_details = {
      'exception': '{}'.format(err),
      'time_reported': datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    }
    if self._lambda_context:
      try:
        err_key['aws']['getRemainingTimeInMillis'] = self._lambda_context.get_remaining_time_in_millis()
      except Exception as aws_lambda_err: pass # @TODO handle this more gracefully

    err_key = 'errors'
    if not self.report.has_key(err_key):
      self.report[err_key] = err_details
    else:
      if not type(self.report[err_key]) == type([]): self[report][err_key] = [ self.report[err_key] ]

      self.report[err_key].append(err_details)

  def send(self):
    """
    Send the current report to IOPipe
    """
    try:
      response = requests.post('https://metrics-api.iopipe.com/v0/event', data=json.dumps(self.report))
      print('POST response: {}'.format(response))
      print(json.dumps(self.report, indent=2))
      self._sent = True
    except Exception as err:
      print('Error reporting metrics to IOPipe. {}'.format(err))
      print(json.dumps(self.report, indent=2))