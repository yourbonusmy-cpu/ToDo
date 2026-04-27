from core.models import GroupTemplate, TaskTemplate


def sync_groups(user, items):
    templates_map = {t.uuid: t for t in TaskTemplate.objects.filter(owner=user)}

    existing = {g.uuid: g for g in GroupTemplate.objects.filter(owner=user)}

    for data in items:
        uuid = data["uuid"]

        obj = existing.get(uuid)

        if obj:
            obj.title = data.get("title", obj.title)
            obj.description = data.get("description", obj.description)
            obj.save()

        else:
            obj = GroupTemplate.objects.create(
                owner=user,
                uuid=uuid,
                title=data.get("title", ""),
            )

        # M2M sync
        task_uuids = data.get("task_uuids", [])

        obj.tasks.set([templates_map[u] for u in task_uuids if u in templates_map])
