def get(data, key, default=None):
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


def map_block(data):
    return {
        "uuid": get(data, "uuid"),
        "title": get(data, "title", ""),
        "priority": get(data, "priority", 0),
        "updated_at": get(data, "updated_at"),
    }


def map_task(data):
    return {
        "uuid": get(data, "uuid"),
        "block_uuid": get(data, "block_uuid"),
        "title": get(data, "title", ""),
        "position": get(data, "position", 0),
        "updated_at": get(data, "updated_at"),
    }
