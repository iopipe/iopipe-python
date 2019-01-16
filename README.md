# IOpipe Analytics & Distributed Tracing Agent for Python

[![Build Status][1]][2] [![Code Coverage][3]][4] [![PyPI Version][5]][6] [![Apache 2.0][7]][8] [![Slack][9]][10]

[1]: https://circleci.com/gh/iopipe/iopipe-python.svg?style=svg
[2]: https://circleci.com/gh/iopipe/iopipe-python
[3]: https://codecov.io/gh/iopipe/iopipe-python/branch/master/graph/badge.svg
[4]: https://codecov.io/gh/iopipe/iopipe-python
[5]: https://badge.fury.io/py/iopipe.svg
[6]: https://badge.fury.io/py/iopipe
[7]: https://img.shields.io/badge/License-Apache%202.0-blue.svg
[8]: https://github.com/iopipe/iopipe-python/blob/master/LICENSE
[9]: https://img.shields.io/badge/chat-slack-ff69b4.svg
[10]: https://iopipe.now.sh

This package provides analytics and distributed tracing for event-driven applications running on AWS Lambda.

- [Installation](https://github.com/iopipe/iopipe-python#installation)
- [Usage](https://github.com/iopipe/iopipe-python#usage)
  - [Configuration](https://github.com/iopipe/iopipe-python#configuration)
  - [Reporting Exceptions](https://github.com/iopipe/iopipe-python#reporting-exceptions)
  - [Custom Metrics](https://github.com/iopipe/iopipe-python#custom-metrics)
  - [Labels](https://github.com/iopipe/iopipe-python#labels)
  - [Core Agent](https://github.com/iopipe/iopipe-python#core-agent)
- [Plugins](https://github.com/iopipe/iopipe-python#plugins)
  - [Event Info Plugin](https://github.com/iopipe/iopipe-python#event-info-plugin)
  - [Logger Plugin](https://github.com/iopipe/iopipe-python#logger-plugin)
  - [Profiler Plugin](https://github.com/iopipe/iopipe-python#profiler-plugin)
  - [Trace Plugin](https://github.com/iopipe/iopipe-python#trace-plugin)
  - [Creating Plugins](https://github.com/iopipe/iopipe-python#creating-plugins)
- [Supported Python Versions](https://github.com/iopipe/iopipe-python#supported-python-versions)
- [Lambda Layers](https://github.com/iopipe/iopipe-python#lambda-layers)
- [Framework Integration](https://github.com/iopipe/iopipe-python#framework-integration)
  - [Chalice](https://github.com/iopipe/iopipe-python#chalice)
  - [Serverless](https://github.com/iopipe/iopipe-python#serverless)
  - [Zappa](https://github.com/iopipe/iopipe-python#zappa)
- [Contributing](https://github.com/iopipe/iopipe-python#contributing)
- [Running Tests](https://github.com/iopipe/iopipe-python#running-tests)
- [License](https://github.com/iopipe/iopipe-python#license)

## Installation

We expect you will import this library into an existing (or new) Python project intended to be run on AWS Lambda.  On Lambda, functions are expected to include module dependencies within their project paths, thus we use `-t $PWD`. Users building projects with a requirements.txt file may simply add `iopipe` to their dependencies.

From your project directory:

```bash
$ pip install iopipe -t .

# If running locally or in other environments _besides_ AWS Lambda:
$ pip install jmespath>=0.7.1,<1.0.0 requests -t .
```

Your folder structure for the function should look similar to:

```
index.py # contains your lambda handler
  /iopipe
    - __init__.py
    - iopipe.py
  /requests
    - __init__.py
    - api.py
    - ...
```

Installation of the requests library is necessary for local dev/test, but not when running on AWS Lambda as this library is part of the default environment via the botocore library.

More details about lambda deployments are available in the [AWS documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html).

## Usage

Simply use our decorator to report metrics:

```python
from iopipe import IOpipe

iopipe = IOpipe('your project token here')

@iopipe
def handler(event, context):
  pass
```

 The agent comes preloaded with the [Event Info](https://github.com/iopipe/iopipe-python#event-info-plugin), [Profiler](https://github.com/iopipe/iopipe-python#profiler-plugin) and [Trace](https://github.com/iopipe/iopipe-python#trace-plugin) plugins. See the relevant plugin sections for usage.

### Configuration

The following may be set as kwargs to the IOpipe class initializer:

#### `token` (string: required)

Your IOpipe project token. If not supplied, the environment variable `$IOPIPE_TOKEN` will be used if present. [Find your project token](https://dashboard.iopipe.com/install)

#### `debug` (bool: optional = False)

Debug mode will log all data sent to IOpipe servers. This is also a good way to evaluate the sort of data that IOpipe is receiving from your application. If not supplied, the environment variable `IOPIPE_DEBUG` will be used if present.

#### `enabled` (bool: optional = True)

Conditionally enable/disable the agent. For example, you will likely want to disabled the agent during development. The environment variable `$IOPIPE_ENABLED` will also be checked.

#### `network_timeout` (int: optional = 5000)

The number of milliseconds IOpipe will wait while sending a report before timing out. If not supplied, the environment variable `$IOPIPE_NETWORK_TIMEOUT` will be used if present.

#### `timeout_window` (int: optional = 500)

By default, IOpipe will capture timeouts by exiting your function 500 milliseconds early from the AWS configured timeout, to allow time for reporting. You can disable this feature by setting `timeout_window` to `0` in your configuration. If not supplied, the environment variable `$IOPIPE_TIMEOUT_WINDOW` will be used if present.

### Reporting Exceptions

The IOpipe decorator will automatically catch, trace and reraise any uncaught exceptions in your function. If you want to trace exceptions raised in your case, you can use the `.error(exception)` method. This will add the exception to the current report.

```python
from iopipe import IOpipe

iopipe = IOpipe()

# Example 1: uncaught exceptions

@iopipe
def handler(event, context):
  raise Exception('This exception will be added to the IOpipe report automatically')

# Example 2: caught exceptions

@iopipe
def handler(event, context):
  try:
    raise Exception('This exception is being caught by your function')
  except Exception as e:
    # Makes sure the exception is added to the report
    context.iopipe.error(e)
```

It is important to note that a report is sent to IOpipe when `error()` is called. So you should only record exceptions this way for failure states. For caught exceptions that are not a failure state, it is recommended to use custom metrics (see below).

### Custom Metrics

You can log custom values in the data sent upstream to IOpipe using the following syntax:

```python
from iopipe import IOpipe

iopipe = IOpipe()

@iopipe
def handler(event, context):
  # the name of the metric must be a string
  # numerical (int, long, float) and string types supported for values
  context.iopipe.metric('my_metric', 42)
```

Metric key names are limited to 128 characters, and string values are limited to 1024 characters.

### Labels

Label invocations sent to IOpipe by calling the `label` method with a string (limit of 128 characters):

```python
from iopipe import IOpipe

iopipe = IOpipe()

@iopipe
def handler(event, context):
  # the name of the tag must be a string
  context.iopipe.label('this-invocation-is-special')
```

### Core Agent

By default, the IOpipe agent comes pre-loaded with all the bundled plugins in `iopipe.contrib.*`. If you prefer to run the agent without plugins or configure which plugins are used, you can use `IOpipeCore`:

```python
from iopipe import IOpipeCore
from iopipe.contrib.trace import TracePlugin

# Load IOpipe with only the trace plugin
iopipe = IOpipeCore(plugins=[TracePlugin()])

@iopipe
def handler(event, context):
pass
```

## Plugins

IOpipe's functionality can be extended through plugins. Plugins hook into the agent lifecycle to allow you to perform additional analytics.

### Event Info Plugin

The IOpipe agent comes bundled with an event info plugin that automatically extracts useful information from the `event`
object and creates custom metrics for them.

Here's an example of how to use the event info plugin:

```python
from iopipe import IOpipe
from iopipe.contrib.eventinfo import EventInfoPlugin

iopipe = IOpipe(plugins=[EventInfoPlugin()])

@iopipe
def handler(event, context):
    # do something here
```

When this plugin is installed, custom metrics will be created automatically for the following event source data:

* API Gateway
* Alexa Skill Kit
* CloudFront
* Kinesis
* Kinesis Firehose
* S3
* SES
* SNS
* SQS
* Scheduled Events

Now in your IOpipe invocation view you will see useful event information.

### Logger Plugin

**Note:** This plugin is in beta. Want to give it a try? Find us on [![Slack](https://img.shields.io/badge/chat-slack-ff69b4.svg)](https://iopipe.now.sh).

The IOpipe agent comes bundled with a logger plugin that allows you to attach IOpipe to the `logging` module so that you can see your log messages in the IOpipe dashboard.

Here's an example of how to use the logger plugin:

```python
from iopipe import IOpipe
from iopipe.contrib.logger import LoggerPlugin

iopipe = IOpipe(plugins=[LoggerPlugin(enabled=True)])

@iopipe
def handler(event, context):
    context.iopipe.log.info('Handler has started execution')
```

Since this plugin adds a handler to the `logging` module, you can use `logging` directly as well:

```python
import logging

from iopipe import IOpipe
from iopipe.contrib.logger import LoggerPlugin

iopipe = IOpipe(plugins=[LoggerPlugin(enabled=True)])
logger = logging.getLogger()

@iopipe
def handler(event, context):
    logger.error('Uh oh')
```

You can also specify a log name, such as if you only wanted to log messages for `mymodule`:

```python
from iopipe import IOpipe
from iopipe.contrib.logger import LoggerPlugin

iopipe = IOpipe(plugins=[LoggerPlugin('mymodule', enabled=True)])
```

This would be equivalent to `logging.getLogger('mymodule')`.

By default the logger plugin is disabled. You must explicitly set `enabled=True` when instantiating or use the `IOPIPE_LOGGER_ENABLED` environment variable to enable it.

The default logger plugin log level is `logging.INFO`, but it can be set like this:

```python
import logging

from iopipe import IOpipe
from iopipe.contrib.logger import LoggerPlugin

iopipe = IOpipe(plugins=[LoggerPlugin(enabled=True, level=logging.DEBUG)])
```

Putting IOpipe into `debug` mode also sets the log level to `logging.DEBUG`.

The logger plugin also redirects stdout by default, so you can do the following:

```python
from iopipe import IOpipe
from iopipe.contrib.logger import LoggerPlugin

iopipe = IOpipe(plugins=[LoggerPlugin(enabled=True)])

@iopipe
def handler(event, context):
    print('I will be logged')
```

Now in your IOpipe invocation view you will see log messages for that invocation.

If you prefer your print statements not to be logged, you can disable this by setting `redirect_stdout` to `False`:

```python
iopipe = IOpipe(plugins=[LoggerPlugin(enabled=True, redirect_stdout=False)])
```

**Note:** Due to a change to the way the python3.7 runtime configures logging, stdout redirection is disabled for this runtime. Use `context.iopipe.log.*` instead.

By default the logger plugin will log messages to an in-memory buffer. If you prefer to log messages to your Lambda function's `/tmp` directory:

```python
iopipe = IOpipe(plugins=[LoggerPlugin(enabled=True, use_tmp=True)])
```

With `use_tmp` enabled, the plugin will automatically delete log files written to `/tmp` after each invocation.

### Profiler Plugin

The IOpipe agent comes bundled with a profiler plugin that allows you to profile your functions with [cProfile](https://docs.python.org/3/library/profile.html#module-cProfile).

Here's an example of how to use the profiler plugin:

```python
from iopipe import IOpipe
from iopipe.contrib.profiler import ProfilerPlugin

iopipe = IOpipe(plugins=[ProfilerPlugin()])

@iopipe
def handler(event, context):
    # do something here
```

By default the plugin will be disabled and can be enabled at runtime by setting the `IOPIPE_PROFILER_ENABLED` environment variable to `true`/`True`.

If you want to enable the plugin for all invocations:

```python
iopipe = IOpipe(plugins=[ProfilerPlugin(enabled=True)])
```

Now in your IOpipe invocation view you will see a "Profiling" section where you can download your profiling report.

Once you download the report you can open it using pstat's interactive browser with this command:

```bash
python -m pstats <file here>
```

Within the pstats browser you can sort and restrict the report in a number of ways, enter the `help` command for details. Refer to the [pstats Documentation](https://docs.python.org/3/library/profile.html#module-pstats).

### Trace Plugin

The IOpipe agent comes bundled with a trace plugin that allows you to perform tracing.

Here's an example of how to use the trace plugin:

```python
from iopipe import IOpipe
from iopipe.contrib.trace import TracePlugin

iopipe = IOpipe(plugins=[TracePlugin()])

@iopipe
def handler(event, context):
    context.iopipe.mark.start('expensive operation')
    # do something here
    context.iopipe.mark.end('expensive operation')
```

Or you can use it as a context manager:

```python
from iopipe import IOpipe
from iopipe.contrib.trace import TracePlugin

iopipe = IOpipe(plugins=[TracePlugin()])

@iopipe
def handler(event, context):
    with context.iopipe.mark('expensive operation'):
        # do something here
```

Any block of code wrapped with `start` and `end` or using the context manager will be traced and the data collected will be available on your IOpipe dashboard.

By default, the trace plugin will auto-measure any trace you make. But you can disable this by setting `auto_measure` to `False`:

```python
from iopipe import IOpipe
from iopipe.contrib.trace import TracePlugin

iopipe = IOpipe(plugins=[TracePlugin(auto_measure=False)])

@iopipe
def handler(event, context):
    with context.iopipe.mark('expensive operation'):
        # do something here

    # Manually measure the trace
    context.iopipe.mark.measure('expensive operation')
```

The trace plugin can also trace your HTTP/HTTPS requests automatically. To enable this feature, set `auto_http` to `True` or set the `IOPIPE_TRACE_AUTO_HTTP_ENABLED` environment variable. For example:

```python
iopipe = IOpipe(plugins=[TracePlugin(auto_http=True)])
```

With `auto_http` enabled, you will see traces for any HTTP/HTTPS requests you make within your function on your IOpipe dashboard. Currently this feature only supports the `requests` library, including `boto3` and `botocore` support.

### Creating Plugins

To create an IOpipe plugin you must implement the `iopipe.plugins.Plugin` interface.

Here is a minimal example:

```python
from iopipe.plugins import Plugin


class MyPlugin(Plugin):
    name = 'my-plugin'
    version = '0.1.0'
    homepage = 'https://github.com/iopipe/my-plugin/'
    enabled = True

    def pre_setup(self, iopipe):
        pass

    def post_setup(self, iopipe):
        pass

    def pre_invoke(self, event, context):
        pass

    def post_invoke(self, event, context):
        pass

    def pre_report(self, report):
        pass

    def post_report(self):
        pass
```

As you can see, this plugin doesn't do much. If you want to see a functioning example of a plugin check out the trace plugin at `iopipe.contrib.trace.plugin.TracePlugin`.

#### Plugin Properties

A plugin has the following properties defined:

- `name`: The name of the plugin, must be a string.
- `version`: The version of the plugin, must be a string.
- `homepage`: The URL of the plugin's homepage, must be a string.
- `enabled`: Whether or not the plugin is enabled, must be a boolean.

#### Plugin Methods

A plugin has the following methods defined:

- `pre_setup`: Is called once prior to the agent initialization. Is passed the `iopipe` instance.
- `post_setup`: Is called once after the agent is initialized, is passed the `iopipe` instance.
- `pre_invoke`: Is called prior to each invocation, is passed the `event` and `context` of the invocation.
- `post_invoke`: Is called after each invocation, is passed the `event` and `context` of the invocation.
- `pre_report`: Is called prior to each report being sent, is passed the `report` instance.
- `post_report`: Is called after each report is sent, is passed the `report` instance.

## Supported Python Versions

This package supports Python 2.7, 3.6 and 3.7, the runtimes supported by AWS Lambda.

## Lambda Layers

IOpipe publishes [AWS Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html) which are publicly available on AWS. Using a framework that supports lambda layers (such as SAM or Serverless), you can use the following ARNs for your runtime:

* python3.6, python3.7: `arn:aws:lambda:$REGION:146318645305:layer:IOpipePython:$VERSION_NUMBER`
* python2.7: `arn:aws:lambda:$REGION:146318645305:layer:IOpipePython27:$VERSION_NUMBER`

Where `$REGION` is your AWS region and `$VERSION_NUMBER` is an integer representing the IOpipe release. You can get the version number via the [Releases](https://github.com/iopipe/iopipe-python/releases) page.

Then in your SAM template (for example), you can add:

```yaml
Globals:
  Function:
    Layers:
        - arn:aws:lambda:us-east-1:146318645305:layer:IOpipePython:1
```

And the IOpipe library will be included in your function automatically.

You can also wrap your IOpipe functions without a code change using layers. For example, in your SAM template you can do the following:

```yaml
Resources:
  YourFunctionere:
    Type: 'AWS::Serverless::Function'
    Properties:
      CodeUri: path/to/your/code
      # Automatically wraps the handler with IOpipe
      Handler: iopipe.handler.wrapper
      Runtime: python3.6
      Environment:
        Variables:
          # Specifies which handler IOpipe should run
          IOPIPE_HANDLER: path.to.your.handler
          IOPIPE_TOKEN: 'your token here'
```

We also have an [example app](https://github.com/iopipe/iopipe-python/tree/master/acceptance/serverless-layers) using layers with Serverless. It also demonstrates how to use layers without a code change.

## Framework Integration

IOpipe integrates with popular serverless frameworks. See below for examples. If you don't see a framework you'd like to see supported, please create an issue.

### Chalice

Using IOpipe with the [Chalice](https://github.com/aws/chalice) framework is easy. Wrap your `app` like so:

```python
from chalice import Chalice
from iopipe import IOpipe

iopipe = IOpipe()

app = Chalice(app_name='helloworld')

@app.route('/')
def index():
    return {'hello': 'world'}

# Do this after defining your routes
app = iopipe(app)
```

### Serverless

Using IOpipe with [Serverless](https://github.com/serverless/serverless) is easy.

First, we recommend the [serverless-python-requirements](https://github.com/UnitedIncome/serverless-python-requirements) plugin:

```bash
$ npm install --save-dev serverless-python-requirements
```

This plugin will add `requirements.txt` support to Serverless. Once installed, add the following to your `serverless.yml`:

```yaml
plugins:
  - serverless-python-requirements
```

Then add `iopipe `to your `requirements.txt`:

```bash
$ echo "iopipe" >> requirements.txt
```

Now Serverless will `pip install -r requirements.txt` when packaging your functions.

Keep in mind you still need to add the `@iopipe` decorator to your functions. See [Usage](https://github.com/iopipe/iopipe-python#usage) for details.

Be sure to check out the [serverless-python-requirements](https://github.com/UnitedIncome/serverless-python-requirements) `README` as the plugin has a number of useful features for compiling AWS Lambda compatible Python packages.

If you're using the [serverless-wsgi](https://github.com/logandk/serverless-wsgi) plugin, you will need to wrap the wsgi handler it bundles with your function.

The easiest way to do this is to create a `wsgi_wrapper.py` module in your project's root with the following:

```python
import imp

from iopipe import IOpipe

wsgi = imp.load_source('wsgi', 'wsgi.py')

iopipe = IOpipe()
handler = iopipe(wsgi.handler)
```

Then in your `serverless.yml`, instead of this:

```yaml
functions:
  api:
    handler: wsgi.handler
    ...
```

Use this:

```yaml
functions:
  api:
    handler: wsgi_wrapper.handler
    ...
```

### Zappa

Using IOpipe with [Zappa](https://github.com/Miserlou/Zappa) is easy. In your project add the following:

```python
from iopipe import IOpipe
from zappa.handler import lambda_handler

iopipe = IOpipe()
lambda_handler = iopipe(lambda_handler)
```

Then in your `zappa_settings.json` file include the following:

```js
{
  "lambda_handler": "module.path.to.lambda_handler"
}
```

Where `module-path.to.lambda_handler` is the Python module path to the `lambda_handler` you created above. For example, if you put it in `myproject/__init__.py` the path would be `myproject.lambda_handler`.

## Contributing

Contributions are welcome. We use the [black](https://github.com/ambv/black) code formatter.

```bash
pip install black
```

We recommend using it with [pre-commit](https://pre-commit.com/#install):

```bash
pip install pre-commit
pre-commit install
```

Using these together will auto format your git commits.

## Running Tests

If you have `tox` installed, you can run the Python 2.7 and 3.6 tests with:

```bash
tox
```

If you don't have `tox` installed you can also run:

```bash
python setup.py test
```

We also have make tasks to run tests in `lambci/lambda:build-python` Docker containers:

```bash
make test
```

## License

Apache 2.0
