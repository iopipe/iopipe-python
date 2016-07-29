import sys
import requests

def iopipe(user_config):
  config = {
    url: "https://metrics-api.iopipe.com/v0/event",
    clientId: false
  }
  config.update(user_config)

  def iopipe_decorator(fun):
    def wrapped(event, context):
      report = _measure(config, context)
      err = None
      try:
        result = fun(event, context)
      catch(e):
        result = None
        err = e
      report(err)
      return result
    return wrapped

def _measure(config, context):
  payload = {
    client_id: config.clientId,
    aws: {
      functionName: context.function_name,
      functionVersion: context.function_version,
      memoryLimitInMB: context.memory_limit_in_mb,
      invokedFunctionArn: context.invoked_function_arn,
      awsRequestId: context.aws_request_id,
      logGroupName: context.log_group_name,
      logStreamName: context.log_stream_name
    },
    python: {
      sys: {
        argv: sys.argv,
        byteorder: sys.byteorder,
        builtin_module_names: sys.builtin_module_names,
        executable: sys.executable,
        flags: sys.flags,
        float_info: sys.float_info,
        float_repr_style: sys.float_repr_style,
        check_interval: sys.getcheckinterval(),
        default_encoding: sys.getdefaultencoding(),
        dlopenflags: sys.getdlopenflags(),
        filesystemencoding: sys.getfilesystemencoding(),
        hexversion: sys.hexversion,
        long_info: sys.long_info,
        maxint: sys.maxint,
        maxsize: sys.maxsize,
        maxunicode: sys.maxunicode,
        meta_path: sys.meta_path,
        modules: sys.modules,
        path: sys.path,
        platform: sys.platform,
        prefix: sys.prefix,
        tracebacklimit: sys.tracebacklimit,
        version: sys.version,
        api_version: sys.api_version,
        version_info: sys.version_info
      }
    }
  }
  def report(err):
    time_nanosec = start - time.time()
    payload.update({
      aws: {
        getRemainingTimeInMillis: context.get_remaining_time_in_millis()
      },
      errors: {
        message: err.message
      },
      time_nanosec: time_nanosec,
      timesec:
    })
    r = requests.post(IOPIPE_METRICS_API, data=payload)
  return report
