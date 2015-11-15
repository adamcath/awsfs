import json
from datetime import datetime


def json_serial(obj):
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def to_json(obj):
    return json.dumps(obj, default=json_serial, sort_keys=True, indent=4) + '\n'
