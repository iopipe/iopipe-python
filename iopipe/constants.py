import os
import pkg_resources
import time

COLDSTART = True
MODULE_LOAD_TIME = time.time() * 1000
PROCESS_ID = str(os.getpid())
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
VERSION = pkg_resources.get_distribution('iopipe').version
