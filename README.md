# IOpipe Telemetry Agent for Python

*WARNING*: Work-in-Progress! This module is not yet ready for production. -- @ewindisch < this -- @marknca

This package provides a Python object to send telemetry to the IOpipe platform for application performance monitoring, analytics, and distributed tracing.

## Installation

We expect you will import this library into an existing (or new) Python project
intended to be run on AWS Lambda.  On Lambda, functions are expected to include
module dependencies within their project paths, thus we use `-t $PWD`.

From your project directory:

```
$ pip install https://github.com/iopipe/iopipe-python -t .
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

More details about lambda deployments are available in the [AWS documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html).

## Basic Usage

Simply use our decorator to report metrics:

```python
from iopipe.iopipe import IOpipe
iopipe = IOpipe("your-client-id")

@iopipe.decorator
def handler(event, context)
  pass
```

## Configuration

The following may be set as kwargs to the IOpipe class initializer:

- client_id: your client_id (register at [www.iopipe.com](https://www.iopipe.com)
- debug: enable debug logging.
- url: custom URL for reporting metrics

## Advanced Usage

Instantiate an ```iopipe.IOpipe``` object inside of your function, then
call .err(Exception) and .send() as necessary.

```python
import iopipe.iopipe

def handler(event, context):
  report = iopipe.IOpipe(CLIENT_ID, context)
  pass
```

If you want to report on multiple functions, you can simply pass the IOpipe object from function to function.

### Explicitly Sending Data

When the IOpipe object is destroyed, it will send the data upstream. You can explicitly send the data upstream by calling the `.send()` method of the object. Provide the AWS Lambda context as a parameter to `.send()`, to report AWS Lambda specific metrics.

### Reporting Exceptions

If you want to trace exceptions thrown in your case, you can use the `.err(err)` function. This will add the exception to the current report.

### Logging additional data (ALPHA)

You can add a custom namespace to the data sent upstream to IOpipe using the following syntax;

```python
from iopipe.iopipe import IOpipe
iopipe = IOpipe()

@iopipe.decorator
def handler(event, context):
  iopipe.log("key", "value")
  pass
```

This makes it easy to add custom data and telemetry.

## Copyright

Provided under the Apache-2.0 license. See LICENSE for details.

Copyright 2016, IOpipe, Inc.
