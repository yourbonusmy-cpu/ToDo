from core.models import GroupTemplate


def get_group_templates(request, last_sync):
    qs = GroupTemplate.objects.filter(owner=request.user)

    if last_sync:
        qs = qs.filter(updated_at__gt=last_sync)

    return [
        {
            "uuid": g.uuid,
            "title": g.title,
            "description": g.description,
            "task_uuids": list(g.tasks.values_list("uuid", flat=True)),
            "updated_at": g.updated_at,
            "created_at": g.created_at,
        }
        for g in qs
    ]
