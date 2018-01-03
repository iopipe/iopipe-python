# Honeycomb plugin for iopipe

This plugin sends a copy of the iopipe report to Honeycomb. In order to use this plugin, you must have an account with Honeycomb. You can sign up at https://honeycomb.io/signup.

To enable this plugin, include it and enable it in your initialization of iopipe:

``` python
from iopipe.contrib.honeycomb import HoneycombReport

iopipe = IOpipe(token=mytoken, plugins=[HoneycombReport])
```

The plugin needs some configuration:

* Honeycomb write key (available from https://ui.honeycomb.io/account)
* Honeycomb dataset name (your choice)
* Sample Rate (optional, defaults to 1)

All three of these attributes can be configured via Lambda environment variables (in the same way the IOPipe Token is configured).  Set the following variables:

* Write key: `IOPIPE_HONEYCOMB_WRITEKEY`
* Dataset name: `IOPIPE_HONEYCOMB_DATASET`
* Sample Rate: `IOPIPE_HONEYCOMB_SAMPLE_RATE`

It is strongly advised that (after the dataset has been created) you enable unpacking of nested JSON (configurable at the bottom of the Schema page).

Once the plugin is configured and successfully sending events to Honeycomb, you can augment the events with the iopipe `log` function call. Use it to record any measurements you want to take or attributes of your function you wish to use in Honeycomb. This can include timers, user IDs, log lines indicating branching, and so on.

This plugin also works well with the `TracePlugin` - if you enable it as well, all the tracing data will automatically be included in the reports sent to Honeycomb.

## Troubleshooting

If you set this up and don't see the Honeycomb dataset being created, enable debugging by adding `debug=True` to your `iopipe` initialization:

``` python
iopipe = IOpipe(token=mytoken, debug=True, plugins=[HoneycombReport])
```

After turning on debug logging, you'll have some extra lines available via CloudWatch Logs. The line you'll be interested in is "got response from Honeycomb". For example, if the write key is not getting successfully set, you'll see this: `[DEBUG] 2018-01-02T23:07:00.722Z a3254b9d-f011-11e7-b7fd-351db3c48dd2 got response from Honeycomb: {'body': u'{"error":"unknown Team key - check your credentials"}', 'status_code': 401, 'duration': 197.627, 'metadata': None, 'error': ''}` (by comparison, a successful send to Honeycomb with debugging enabled will have that line but the `'status_code':` will be `200` instead of `401`)
