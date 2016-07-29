IOpipe Telemetry Agent for Python
---------------------------------

*WARNING*: Work-in-Progress! This module is not yet ready for production. -- @ewindisch

This package provides a Python decorator
to send telemetry to the IOpipe platform for
application performance monitoring, analytics,
and distributed tracing.

# Installation

```
echo "iopipe" >> requirements.txt
pip install -r requirements.txt
```

# Usage

Simply decorate your code using `@iopipe`:

```
import iopipe

@iopipe(YOUR_IOPIPE_CLIENTID)
def handler(event, context):
  pass
```

### Wrapping multiple functions.

If wrapping multiple functions, you can set the clientid once
as such:

```
import iopipe as iopipe_module
iopipe = iopipe_module(YOUR_IOPIPE_CLIENTID)

@iopipe
def handler(event, context):
  pass
```

# Copyright

Provided under the Apache-2.0 license. See LICENSE for details.

Copyright 2016, IOpipe, Inc.
