# IOpipe Telemetry Agent for Python

*WARNING*: Work-in-Progress! This module is not yet ready for production. -- @ewindisch

This package provides a Python decorator to send telemetry to the IOpipe platform for application performance monitoring, analytics, and distributed tracing.

## Installation

Simple copy ```iopipe.py``` to your project. It is a self-contained module with no requirements outside of the standard library.

**Update:** Added back Requests library while troubleshooting a 403 error using urllib2. Please make sure that the libs/* directory is included with your AWS Lambda function.

## Usage

Simply decorate your code using ```@iopipe```:

```python
from iopipe import iopipe

@iopipe(YOUR_IOPIPE_CLIENTID)
def handler(event, context):
  pass
```

### Wrapping Multiple Functions

If wrapping multiple functions, you can set the clientid once as such:

```python
from iopipe import iopipe
from iopipe import set_iopipe_global_client_id

set_iopipe_global_client_id(YOUR_IOPIPE_CLIENTID)

@iopipe()
def handler(event, context):
  pass
```

### Custom Namespaces

You can add a custom namespace to the data sent upstream to IOPipe using teh following syntax;

```python
from iopipe import iopipe

@iopipe(YOUR_IOPIPE_CLIENTID, custom_namespace='myspace', custom_data={ 'mykey': 1 })
def handler(event, context):
  pass
```

This makes it easy to add custom data and telemetry.

**@TODO:** Make it possible to add custom data from within the primary AWS Lambda function. Custom data currently needs to be added before the function is wrapped.

## Copyright

Provided under the Apache-2.0 license. See LICENSE for details.

Copyright 2016, IOpipe, Inc.
