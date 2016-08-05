# standard library
import json
import sys
import urllib2

# module level vars
CLIENT_ID = None

def set_iopipe_global_client_id(client_id):
  """
  Set the client_id once for all future decorators in this run
  """
  global CLIENT_ID
  CLIENT_ID = client_id

def iopipe(client_id=None):
  """
  Outer method to allow arguments in the decorator
  """

  # allow the client_id to be set once
  if not client_id and CLIENT_ID:
    client_id = CLIENT_ID
  else:
    print("A client_id is required to send telemetry upstream to IOPipe")

  # ensure that client_id can be passed
  def iopipe_decorator(func): # actual wrapper function
    """
    @iopipe decorator
    """
    def wrapped(event, context):
      """
      Function to execute around the wrapped function
      """
      # event and context are pulled from AWS Lambda
      current_report = _measure(client_id=client_id, lambda_context=context)
      result = None
      try:
        result = func(event, context)
      except Exception as err:
        result = None
        current_report = _measure_exception(report=current_report, lambda_context=context, err=err)

      # send the report to IOPipe
      request = urllib2.Request('https://metrics-api.iopipe.com')
      request.add_header('Content-Type', 'application/json')
      try:
        response = urllib2.urlopen(request, json.dumps(current_report))
        print('POST response: {}'.format(response))
      except urllib2.HTTPError as err:
        print('Error reporting metrics to IOPipe. {}'.format(err))
        print(json.dumps(current_report))

      return result
    return wrapped
  return iopipe_decorator

def _measure(client_id, lambda_context):
  """
  Build a report containing measurements of the current function and it's execution environment
  """
  return {
    'client_id': client_id,
    'aws': { # camel case to align with AWS standards
      'functionName': lambda_context.function_name if 'function_name' in dir(lambda_context) else '',
      'functionVersion': lambda_context.function_version if 'function_version' in dir(lambda_context) else '',
      'memoryLimitInMB': lambda_context.memory_limit_in_mb if 'memory_limit_in_mb' in dir(lambda_context) else '',
      'invokedFunctionArn': lambda_context.invoked_function_arn if 'invoked_function_arn' in dir(lambda_context) else '',
      'awsRequestId': lambda_context.aws_request_id if 'aws_request_id' in dir(lambda_context) else '',
      'logGroupName': lambda_context.log_group_name if 'log_group_name' in dir(lambda_context) else '',
      'logStreamName': lambda_context.log_stream_name if 'log_stream_name' in dir(lambda_context) else '',
    },
    'python': {
      'sys': { # lower_ case to align with python standards
        'argv': sys.argv if 'argv' in dir(sys) else '',
        'byte_order': sys.byteorder if 'byteorder' in dir(sys) else '',
        'builtin_module_names': sys.builtin_module_names if 'builtin_module_names' in dir(sys) else '',
        'executable': sys.executable if 'executable' in dir(sys) else '',
        'flags': '{}'.format(sys.flags) if 'flags' in dir(sys) else '',
        'float_info': '{}'.format(sys.float_info) if 'float_info' in dir(sys) else '',
        'float_repr_style': sys.float_repr_style if 'float_repr_style' in dir(sys) else '',
        'check_interval': sys.getcheckinterval(),
        'default_encoding': sys.getdefaultencoding(),
        'dl_open_flags': sys.getdlopenflags(),
        'file_system_encoding': sys.getfilesystemencoding(),
        'hex_version': sys.hexversion if 'hexversion' in dir(sys) else '',
        'long_info': '{}'.format(sys.long_info) if 'long_info' in dir(sys) else '',
        'max_int': sys.maxint if 'maxint' in dir(sys) else '',
        'max_size': sys.maxsize if 'maxsize' in dir(sys) else '',
        'max_unicode': sys.maxunicode if 'maxunicode' in dir(sys) else '',
        'meta_path': sys.meta_path if 'meta_path' in dir(sys) else '',
        'modules': sys.modules.keys() if 'modules' in dir(sys) else '',
        'path': sys.path if 'path' in dir(sys) else '',
        'platform': sys.platform if 'platform' in dir(sys) else '',
        'prefix': sys.prefix if 'prefix' in dir(sys) else '',
        'traceback_limit': sys.tracebacklimit if 'tracebacklimit' in dir(sys) else '',
        'version': '{}'.format(sys.version) if 'version' in dir(sys) else '',
        'api_version': sys.api_version if 'api_version' in dir(sys) else '',
        'version_info': '{}'.format(sys.version_info) if 'version_info' in dir(sys) else '',
        }
      }
    }

def _measure_exception(report, lambda_context, err):
  """
  Add the details for any exceptions thrown during execution
  """
  report['errors'] = {
      'message': err.message
    }
  report['aws']['getRemainingTimeInMillis'] = lambda_context.get_remaining_time_in_millis()
  report['time_nanosec'] = 0
  report['time_sec'] = 0

  return report