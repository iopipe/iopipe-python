import time
import uuid

COLDSTART = True
MODULE_LOAD_TIME = time.time() * 1000
PROCESS_ID = str(uuid.uuid4())
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
VERSION = '1.0.1'
