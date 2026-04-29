from core.models import Block


def get_blocks(request, last_sync):
    qs = Block.objects.filter(owner=request.user)

    if last_sync:
        qs = qs.filter(updated_at__gt=last_sync)

    return list(
        qs.values(
            "uuid",
            "title",
            "priority",
            "is_hidden",
            "target_date",
            "updated_at",
        )
    )
