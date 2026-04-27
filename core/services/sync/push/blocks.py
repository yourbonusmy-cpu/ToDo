from core.models import Block
from core.services.sync.common.conflict import resolve_update
from core.services.sync.common.time import safe_parse_dt
from core.services.sync.common.uuid import as_uuid_map


def sync_blocks(user, items):
    existing = as_uuid_map(Block.objects.filter(owner=user))

    for data in items:
        uuid = data["uuid"]
        client_time = safe_parse_dt(data.get("updated_at"))

        obj = existing.get(uuid)

        if obj:
            if not resolve_update(obj, data, client_time, obj.updated_at):
                continue

            obj.title = data.get("title", obj.title)
            obj.priority = data.get("priority", obj.priority)
            obj.is_hidden = data.get("is_hidden", obj.is_hidden)
            obj.target_date = data.get("target_date", obj.target_date)
            obj.save()

        else:
            Block.objects.create(
                owner=user,
                uuid=uuid,
                title=data.get("title", ""),
                priority=data.get("priority", 0),
            )
