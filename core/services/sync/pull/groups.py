from core.models import GroupTemplate


def get_groups(user, last_sync):
    qs = GroupTemplate.objects.filter(owner=user)

    if last_sync:
        qs = qs.filter(updated_at__gt=last_sync)

    return [
        {
            "uuid": g.uuid,
            "title": g.title,
            "description": g.description,
            "task_uuids": list(g.tasks.values_list("uuid", flat=True)),
            "updated_at": g.updated_at,
        }
        for g in qs
    ]
