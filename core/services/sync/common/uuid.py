import uuid


def safe_uuid(value):
    try:
        return uuid.UUID(str(value))
    except Exception:
        return None


def as_uuid_map(queryset):
    """
    превращает queryset в {uuid: obj}
    """
    return {obj.uuid: obj for obj in queryset}
