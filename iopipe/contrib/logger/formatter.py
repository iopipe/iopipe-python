import json
import logging
import time


class JSONFormatter(logging.Formatter):
    converter = time.gmtime
    default_time_format = '%Y-%m-%d %H:%M:%S'
    default_msec_format = '%s.%03d'

    def format(self, record):
        record.asctime = self.formatTime(record, self.datefmt)
        record.message = record.getMessage()
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if record.message[-1:] != '\n':
                record.message = record.message + '\n'
            record.message = record.message + record.exc_text
        if hasattr(record, 'stack_info') and record.stack_info:
            if record.message[-1:] != '\n':
                record.message = record.message + '\n'
            record.message = record.message + self.formatStack(record.stack_info)
        return json.dumps({
            'message': record.message,
            'name': record.name,
            'severity': record.levelname,
            'timestamp': record.asctime,
        }, sort_keys=True)
