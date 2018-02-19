from .util import get_value, has_key


class EventType(object):
    def __init__(self, event):
        self.event = event

    def has_required_keys(self):
        return all(has_key(self.event, key) for key in self.required_keys)

    def collect(self):
        event_info = {}
        for key in self.keys:
            value = get_value(self.event, key)
            if value is not None:
                event_info['@iopipe/event-info.%s.%s' % (self.type, key)] = value
        event_info['@iopipe/event-info.eventType'] = self.type
        return event_info


class ApiGateway(EventType):
    type = 'apiGateway'
    keys = [
        'httpMethod',
        'path',
        'requestContext.accountId',
        'requestContext.httpMethod',
        'requestContext.identity.userAgent',
        'requestContext.requestId',
        'requestContext.resourcePath',
        'requestContext.stage',
        'resource',
    ]
    required_keys = [
        'headers',
        'httpMethod',
        'path',
        'requestContext',
        'resource',
    ]


class CloudFront(EventType):
    type = 'cloudFront'
    keys = [
        'Records[0].cf.config.distributionId',
        'Records[0].cf.request.clientIp',
        'Records[0].cf.request.headers.host[0].value',
        'Records[0].cf.request.headers.["user-agent"][0].value',
        'Records[0].cf.request.method',
        'Records[0].cf.request.uri',
    ]
    required_keys = ['Records[0].cf']


class Firehose(EventType):
    type = 'firehose'
    keys = [
        'deliveryStreamArn',
        'region',
    ]
    required_keys = [
        'deliveryStreamArn',
        'records[0]',
        'records[0].kinesisRecordMetadata',
    ]


class Kinesis(EventType):
    type = 'kinesis'
    keys = [
        'Records.length',
        'Records[0].awsRegion',
        'Records[0].eventSourceARN',
    ]
    required_keys = [
        'Records[0].eventVersion',
        'Records[0].eventSource',
    ]

    def has_required_keys(self):
        return super(Kinesis, self).has_required_keys() and \
            get_value(self.event, 'Records[0].eventVersion') == '1.0' and \
            get_value(self.event, 'Records[0].eventSource') == 'aws:kinesis'


class S3(EventType):
    type = 's3'
    keys = [
        'Records[0].awsRegion',
        'Records[0].eventName',
        'Records[0].eventTime',
        'Records[0].requestParameters.sourceIPAddress',
        'Records[0].responseElements["x-amz-id-2"]',
        'Records[0].responseElements["x-amz-request-id"]',
        'Records[0].s3.bucket.arn',
        'Records[0].s3.bucket.name',
        'Records[0].s3.object.key',
        'Records[0].s3.object.sequencer',
        'Records[0].s3.object.size',
        'Records[0].userIdentity.principalId',
    ]
    required_keys = [
        'Records[0].eventVersion',
        'Records[0].eventSource',
    ]

    def has_required_keys(self):
        return super(S3, self).has_required_keys() and \
            get_value(self.event, 'Records[0].eventVersion') == '2.0' and \
            get_value(self.event, 'Records[0].eventSource') == 'aws:s3'


class Scheduled(EventType):
    type = 'scheduled'
    keys = [
        'account',
        'id',
        'region',
        'resources[0]',
        'time',
    ]
    required_keys = ['source']

    def has_required_keys(self):
        return super(Scheduled, self).has_required_keys() and get_value(self.event, 'source') == 'aws.events'


class SNS(EventType):
    type = 'sns'
    keys = [
        'Records[0].EventSubscriptionArn',
        'Records[0].Sns.MessageId',
        'Records[0].Sns.Signature',
        'Records[0].Sns.SignatureVersion',
        'Records[0].Sns.SigningCertUrl',
        'Records[0].Sns.UnsubscribeUrl',
        'Records[0].Sns.Subject',
        'Records[0].Sns.Timestamp',
        'Records[0].Sns.TopicArn',
        'Records[0].Sns.Type',
    ]
    required_keys = [
        'Records[0].eventVersion',
        'Records[0].eventSource',
    ]

    def has_required_keys(self):
        return super(SNS, self).has_required_keys() and \
            get_value(self.event, 'Records[0].eventVersion') == '1.0' and \
            get_value(self.event, 'Records[0].eventSource') == 'aws:sns'


EVENT_TYPES = [ApiGateway, CloudFront, Firehose, Kinesis, S3, Scheduled, SNS]


def log_for_event_type(event, log):
    for EventType in EVENT_TYPES:
        event_type = EventType(event)
        if event_type.has_required_keys():
            event_info = event_type.collect()
            [log(k, v) for k, v in event_info.items()]
            break
