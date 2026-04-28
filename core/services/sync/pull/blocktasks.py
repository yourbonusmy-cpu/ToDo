from core.models import BlockTask


def get_blocktasks(user, last_sync):
    qs = BlockTask.objects.filter(block__owner=user)

    if last_sync:
        qs = qs.filter(updated_at__gt=last_sync)

    return list(
        qs.values(
            "uuid",
            "block__uuid",
            "template__uuid",
            "title",
            "description",
            "amount",
            "time",
            "position",
            "is_hidden",
            "is_encrypted",
            "icon",
            "updated_at",
        )
    )
