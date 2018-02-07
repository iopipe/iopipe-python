from .event_types import EVENT_TYPES


def get_nested(obj, *path):
    for p in path:
        if p == 'length':
            return len(obj)
        first_item = p.endswith('[0]')
        if first_item:
            p = p.replace('[0]', '')
        if p not in obj:
            return
        obj = obj.get(p)
        if first_item:
            if not isinstance(obj, list) or not len(obj) > 0:
                return
            obj = obj[0]
    return obj


def log_for_event_type(event, log):
    for EventType in EVENT_TYPES:
        event_type = EventType(event)
        if event_type.has_required_keys():
            event_info = event_type.collect()
            (log(k, v) for k, v in event_info.items())
            break
