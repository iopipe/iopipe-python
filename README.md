# IOpipe Telemetry Agent for Python

This package provides a Python object to send telemetry to the IOpipe platform for application performance monitoring, analytics, and distributed tracing.

## Maintenance Notice

This project is on hiatus so that we at IOpipe can focus on our core functionality until such time as we have the resources to devote to giving our users a truly top-notch Python agent. This module will remain *in alpha state* until that time. We will still accept issue reports/pull requests, and will respond as quickly as we can to either. We appreciate your patience.

## Installation

We expect you will import this library into an existing (or new) Python project
intended to be run on AWS Lambda.  On Lambda, functions are expected to include
module dependencies within their project paths, thus we use `-t $PWD`. Users
building projects with a requirements.txt file may simply add `iopipe` to their
dependencies.

From your project directory:

```
$ pip install iopipe -t .

# If running locally or in other environments _besides_ AWS Lambda:
$ pip install requests -t iopipe/requests
```

Your folder structure for the function should look similar to;

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

Installation of the requests library is necessary for local dev/test, but not
when running on AWS Lambda as this library is part of the default environment
via the botocore library.

More details about lambda deployments are available in the [AWS documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html).

## Basic Usage

Simply use our decorator to report metrics:

```python
from iopipe.iopipe import IOpipe
iopipe = IOpipe("your-client-id")

@iopipe.decorator
def handler(event, context):
  pass
```

## Configuration

The following may be set as kwargs to the IOpipe class initializer:

- client_id: your client_id (register at [www.iopipe.com](https://www.iopipe.com)
- debug: enable debug logging by setting this to `True`
- url: custom URL for reporting metrics

## Advanced Usage

Instantiate an `iopipe.IOpipe` object inside of your function, then
call .err(Exception) and .send() to report data and exceptions.

We recommend using our handy decorator instead.

```python
from iopipe.iopipe import IOpipe

def handler(event, context):
  iopipe = IOpipe(CLIENT_ID)
  timestamp = time.time()
  report = iopipe.create_report(timestamp, context)

  try:
    # do some things
  except Exception as e:
    iopipe.err(e)

  report.send()
```

If you want to report on multiple functions, you can simply pass the IOpipe object from function to function.

### Reporting Exceptions

If you want to trace exceptions thrown in your case, you can use the `.err(err)` function. This will add the exception to the current report.

### Custom Metrics

You can log custom values in the data sent upstream to IOpipe using the following syntax:

```python
from iopipe.iopipe import IOpipe
iopipe = IOpipe()

@iopipe.decorator
def handler(event, context):
  # the name of the metric must be a string
  # numerical (int, long, float) and string types supported for values
  iopipe.log("my_metric", 42)
  pass
```

This makes it easy to add custom data and telemetry within your function.

### Disabling IOpipe

If you need to disable IOpipe monitoring during development or in any other situation you can set `IOPIPE_ENABLED` environment variable to `False`.

Default for `IOPIPE_ENABLED` environment variable is `True`.

## Copyright

Provided under the Apache-2.0 license. See LICENSE for details.

Copyright 2016-2017, IOpipe, Inc.
