from core.models import TaskTemplate


def sync_templates(user, items):
    existing = {t.uuid: t for t in TaskTemplate.objects.filter(owner=user)}

    for data in items:
        uuid = data["uuid"]

        obj = existing.get(uuid)

        if obj:
            obj.title = data.get("title", obj.title)
            obj.description = data.get("description", obj.description)
            obj.priority = data.get("priority", obj.priority)
            obj.is_hidden = data.get("is_hidden", obj.is_hidden)
            obj.save()

        else:
            TaskTemplate.objects.create(
                owner=user,
                uuid=uuid,
                title=data.get("title", ""),
            )
