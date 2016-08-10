import datetime
import json
import os
import sys
import time

import requests

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DEFAULT_ENDPOINT_URL = "https://metrics-api.iopipe.com"


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
    if not self._sent: self.send()

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

    if context and 'get_remaining_time_in_millis' in context:
      try:
        self.report['aws']['getRemainingTimeInMillis'] = context.get_remaining_time_in_millis()
      except Exception as aws_lambda_err: pass # @TODO handle this more gracefully

  def _add_python_local_data(self, get_all=False):
    """
    Add the python sys attributes relevant to AWS Lambda execution
    """
    self.report['environment'] = {}
    self.report['environment']['python'] = {}
    self.report['environment']['python']['sys'] = {}

    sys_attr = {}
    if get_all: # full set of data
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
    else: # reduced set of data for common cases
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
        self.report['environment']['python']['sys'][k] = "{}".format(getattr(sys, v))
 
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
          self.report['environment']['python']['sys'][k] = "{}".format(getattr(sys, v)())

    # convert sys.modules to something more usable
    self.report['environment']['python']['sys']['modules'] = {}
    for k, v in sys.modules.items():
      val = ""
      if '__file__' in dir(v):
        val = v.__file__
      elif '__path__' in dir(v):
        val = v.__path__ 

      self.report['environment']['python']['sys']['modules'][k] = val

  def log(self, key, value):
    """
    Add custom data to the report
    """
    # make sure the namespace exists
    if not self.report.has_key('events'): self.report['events'] = {}

    if self.report['events'].has_key(key):
      # the key exists, merge the data
      if type(self.report['events'][key]) == type([]):
        self.report['events'][key].append(value)
      else:
        self.report['events'][key] = [ self.report['events'][key], value ]
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
    if not self.report.has_key('errors'):
      self.report['errors'] = err_details
    elif type(self.report['errors']) != type([]):
      self[report]['errors'] = [ self.report['errors'] ]

    self.report['errors'].append(err_details)

    # add the full local python data as well
    self._add_python_local_data(get_all=True)

  def send(self, context=None):
    """
    Send the current report to IOpipe
    """
    json_report = None

    # Duration of execution.
    self.report['time_nanosec'] = time.time() - self._time_start

    if context:
      self._add_aws_lambda_data(context)
    self._add_python_local_data()

    try:
      json_report = json.dumps(self.report, indent=2)
    except Exception as err:
      print("Could not convert the report to JSON. Threw exception: {}".format(err))
      print('Report: {}'.format(self.report))
      return

    try:
      response = requests.post(self._url + '/v0/event', data=json_report, headers={ "Content-Type": "application/json" })
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
      return result
    return wrapped
