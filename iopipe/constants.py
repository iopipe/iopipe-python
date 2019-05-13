import time
import uuid

COLDSTART = True
MODULE_LOAD_TIME = time.time() * 1000
PROCESS_ID = str(uuid.uuid4())
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
METRIC_NAME_LIMIT = 128
VERSION = "1.7.18"
