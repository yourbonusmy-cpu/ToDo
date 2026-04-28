from core.models import BlockTask


def get_block_tasks(user, last_sync):
    qs = BlockTask.objects.filter(block__owner=user)

    if last_sync:
        qs = qs.filter(updated_at__gt=last_sync)

    data = list(
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
            "created_at",
        )
    )

    for item in data:
        if item["icon"]:
            item["icon"] = f"media/{item['icon']}"

    return data
