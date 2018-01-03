import logging
import libhoney

logger = logging.getLogger(__name__)

def format_report(report):
    """
    Munges the report format to be more honeycomb-friendly
    """
    # munge custom metrics
    if 'custom_metrics' in report:
        custom = {}
        for log in report['custom_metrics']:
            name = log['name']
            # undo decimal typecast to strings
            if 'n' in log:
                val = log['n']
            elif 's' in log:
                val = log['s']
            else:
                val = None
                custom['hny_translation_err'] = "not_n_or_s for key {}".format(name)
            custom[name] = val
        report['custom'] = custom

    # munge tracing plugin's contributions. this will likely need improvement
    # for example, could pull out matching start/end segments and calculate stuff...
    # [{"duration":0,"entryType":"mark","name":"start:iopipe","startTime":24674,"timestamp":1514940704792},
    # {"duration":0,"entryType":"mark","name":"end:iopipe","startTime":3229406,"timestamp":1514940704795}]
    if 'performanceEntries' in report:
        traces = {}
        for mark in report['performanceEntries']:
            trace = {
                "duration": mark['duration'],
                "entryType": mark['entryType'],
                "startTime": mark['startTime'],
                "timestamp": mark['timestamp'],
            }
            traces[mark['name']] = trace
        report['traces'] = traces


def send_honeycomb(report, config):
    """
    Sends the report to Honeycomb.

    :param report: The report to be sent.
    :param config: The IOpipe agent configuration.
    """

    try:
        ev = libhoney.Event()
        ev.add(report)
        ev.send()
    except Exception as e:
        logger.info('Error sending report to Honeycomb: %s' % e)

