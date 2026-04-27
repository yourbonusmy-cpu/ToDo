from core.models import DeletedObject


def get_deleted(user, last_sync):
    qs = DeletedObject.objects.filter(user=user)

    if last_sync:
        qs = qs.filter(deleted_at__gt=last_sync)

    return list(
        qs.values(
            "obj_uuid",
            "object_type",
            "deleted_at",
        )
    )
