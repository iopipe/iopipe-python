import logging
import libhoney

logger = logging.getLogger(__name__)

def send_honeycomb(report, config):
    """
    Sends the report to Honeycomb.

    :param report: The report to be sent.
    :param config: The IOpipe agent configuration.
    """

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
    try:
        ev = libhoney.Event()
        ev.add(report)
        ev.send()
    except Exception as e:
        logger.info('Error sending report to Honeycomb: %s' % e)

