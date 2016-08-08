# IOpipe Telemetry Agent for Python

*WARNING*: Work-in-Progress! This module is not yet ready for production. -- @ewindisch < this -- @marknca

This package provides a Python object to send telemetry to the IOpipe platform for application performance monitoring, analytics, and distributed tracing.

## Installation

Currently you need to include the ```iopipe.py``` and ```libs/``` directory in your AWS Lambda function. Removing the requirement for external libraries is on the short term @TODO list.

## Usage

Simply instantiate an ```iopipe.Report``` object inside of your function.

```python
import iopipe

def handler(event, context):
  report = iopipe.Report(CLIENT_ID, context)
  pass
```

If you want to report on multiple functions, you can simply pass the iopipe.Report object from function to function.

### Explicitly Sending Data

When the iopipe.Report object is destroyed, it will send the data upstream. You can explicitly send the data upstream by calling the ```.send()``` method of the object.

### Reporting Exceptions

If you want to trace exceptions thrown in your case, you can use the ```.report_err(err)``` function. This will automatically add the exception to the current report.

### Custom Namespaces

You can add a custom namespace to the data sent upstream to IOPipe using the following syntax;

```python
import iopipe

def handler(event, context):
  report = iopipe.Report(CLIENT_ID, context, custom_data_namespace='MySpace')
  report.add_custom_data('custom_key', 'custom_value')
  pass
```

This makes it easy to add custom data and telemetry.

## Copyright

Provided under the Apache-2.0 license. See LICENSE for details.

Copyright 2016, IOpipe, Inc.
