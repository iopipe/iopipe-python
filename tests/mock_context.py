class MockContext(object):
    function_version = '$LATEST'
    aws_request_id = '0'
    log_group_name = 'mock-group'
    log_stream_name = 'mock-stream'
    memory_limit_in_mb = 500

    def __init__(self, name='handler', version='$LATEST'):
        self.function_name = name
        self.function_version = version
        self.invoked_function_arn = """arn:aws:lambda:us-east-1:1:
            function:%s:%s""" % (name, version)

    def get_remaining_time_in_millis(self):
        return float('inf')
