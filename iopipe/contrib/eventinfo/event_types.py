from .util import collect_all_keys, get_value, has_key, slugify


class EventType(object):
    keys = []
    exclude_keys = []
    required_keys = []
    source = None

    def __init__(self, event):
        self.event = event

    @property
    def slug(self):
        return slugify(self.type)

    def has_required_keys(self):
        return all(has_key(self.event, key) for key in self.required_keys)

    def collect(self):
        if self.keys == "all":
            event_info = collect_all_keys(
                self.event, "@iopipe/event-info.%s" % self.type, self.exclude_keys
            )
            event_info["@iopipe/event-info.eventType"] = self.type
            return event_info

        event_info = {}
        for key in self.keys:
            if isinstance(key, tuple):
                old_key, new_key = key
            else:
                old_key = new_key = key
            value = get_value(self.event, old_key)
            if value is not None:
                event_info["@iopipe/event-info.%s.%s" % (self.type, new_key)] = value
        event_info["@iopipe/event-info.eventType"] = self.type
        if self.source:
            event_info["@iopipe/event-info.eventType.source"] = self.source
        return event_info


class AlexaSkill(EventType):
    type = "alexaSkill"
    keys = "all"
    exclude_keys = [
        "context.System.apiAccessToken",
        "context.System.user.accessToken",
        "context.System.user.permissions.consentToken",
    ]
    required_keys = [
        "context.System",
        "request.requestId",
        "session.attributes",
        "session.user",
    ]


class ApiGateway(EventType):
    type = "apiGateway"
    keys = [
        "httpMethod",
        "path",
        "requestContext.accountId",
        "requestContext.httpMethod",
        "requestContext.identity.userAgent",
        "requestContext.requestId",
        "requestContext.resourcePath",
        "requestContext.stage",
        "resource",
    ]
    required_keys = ["headers", "httpMethod", "path", "requestContext", "resource"]


class CloudFront(EventType):
    type = "cloudFront"
    keys = [
        "Records[0].cf.config.distributionId",
        "Records[0].cf.request.clientIp",
        "Records[0].cf.request.headers.host[0].value",
        'Records[0].cf.request.headers.["user-agent"][0].value',
        "Records[0].cf.request.method",
        "Records[0].cf.request.uri",
    ]
    required_keys = ["Records[0].cf"]


class Firehose(EventType):
    type = "firehose"
    keys = ["deliveryStreamArn", "region"]
    required_keys = [
        "deliveryStreamArn",
        "records[0]",
        "records[0].kinesisRecordMetadata",
    ]


class Kinesis(EventType):
    type = "kinesis"
    keys = ["Records.length", "Records[0].awsRegion", "Records[0].eventSourceARN"]
    required_keys = ["Records[0].eventVersion", "Records[0].eventSource"]

    def has_required_keys(self):
        return (
            super(Kinesis, self).has_required_keys()
            and get_value(self.event, "Records[0].eventVersion") == "1.0"
            and get_value(self.event, "Records[0].eventSource") == "aws:kinesis"
        )


class S3(EventType):
    type = "s3"
    keys = [
        "Records[0].awsRegion",
        "Records[0].eventName",
        "Records[0].eventTime",
        "Records[0].requestParameters.sourceIPAddress",
        'Records[0].responseElements["x-amz-id-2"]',
        'Records[0].responseElements["x-amz-request-id"]',
        "Records[0].s3.bucket.arn",
        "Records[0].s3.bucket.name",
        "Records[0].s3.object.key",
        "Records[0].s3.object.sequencer",
        "Records[0].s3.object.size",
        "Records[0].userIdentity.principalId",
    ]
    required_keys = ["Records[0].eventVersion", "Records[0].eventSource"]

    def has_required_keys(self):
        return (
            super(S3, self).has_required_keys()
            and get_value(self.event, "Records[0].eventVersion") in ("2.0", "2.1")
            and get_value(self.event, "Records[0].eventSource") == "aws:s3"
        )


class Scheduled(EventType):
    type = "scheduled"
    keys = ["account", "id", "region", "resources[0]", "time"]
    required_keys = ["source"]

    def has_required_keys(self):
        return (
            super(Scheduled, self).has_required_keys()
            and get_value(self.event, "source") == "aws.events"
        )


class ServerlessLambda(EventType):
    type = "apiGateway"
    source = "slsIntegrationLambda"
    keys = [
        ('headers.["X-Amz-Cf-Id"]', "headers.X-Amz-Cf-Id"),
        ('headers.["X-Amzn-Trace-Id"]', "headers.X-Amzn-Trace-Id"),
        ("identity.accountId", "requestContext.accountId"),
        ("identity.userAgent", "requestContext.identity.userAgent"),
        ("method", "httpMethod"),
        ("method", "requestContext.httpMethod"),
        ("stage", "requestContext.stage"),
    ]
    required_keys = ["identity.userAgent", "identity.sourceIp", "identity.accountId"]


class SNS(EventType):
    type = "sns"
    keys = [
        "Records[0].EventSubscriptionArn",
        "Records[0].Sns.MessageId",
        "Records[0].Sns.Signature",
        "Records[0].Sns.SignatureVersion",
        "Records[0].Sns.SigningCertUrl",
        "Records[0].Sns.UnsubscribeUrl",
        "Records[0].Sns.Subject",
        "Records[0].Sns.Timestamp",
        "Records[0].Sns.TopicArn",
        "Records[0].Sns.Type",
    ]
    required_keys = ["Records[0].EventVersion", "Records[0].EventSource"]

    def has_required_keys(self):
        return (
            super(SNS, self).has_required_keys()
            and get_value(self.event, "Records[0].EventVersion") == "1.0"
            and get_value(self.event, "Records[0].EventSource") == "aws:sns"
        )


class SQS(EventType):
    type = "sqs"
    keys = [
        "Records[0].attributes.ApproximateFirstReceiveTimestamp",
        "Records[0].attributes.ApproximateReceiveCount",
        "Records[0].attributes.SenderId",
        "Records[0].attributes.SentTimestamp",
        "Records[0].awsRegion",
        "Records[0].eventSourceARN",
        "Records[0].md5OfBody",
        "Records[0].messageId",
        "Records[0].receiptHandle",
    ]
    required_keys = ["Records[0].eventSource"]

    def has_required_keys(self):
        return (
            super(SQS, self).has_required_keys()
            and get_value(self.event, "Records[0].eventSource") == "aws:sqs"
        )


EVENT_TYPES = [
    AlexaSkill,
    ApiGateway,
    CloudFront,
    Firehose,
    Kinesis,
    S3,
    Scheduled,
    ServerlessLambda,
    SNS,
    SQS,
]


def metrics_for_event_type(event, context):
    for EventType in EVENT_TYPES:
        event_type = EventType(event)
        if event_type.has_required_keys():
            context.iopipe.label("@iopipe/plugin-event-info")
            context.iopipe.label("@iopipe/aws-%s" % event_type.slug)
            context.iopipe.event_type("aws-%s" % event_type.slug)
            event_info = event_type.collect()
            [context.iopipe.metric(k, v) for k, v in event_info.items()]
            break
