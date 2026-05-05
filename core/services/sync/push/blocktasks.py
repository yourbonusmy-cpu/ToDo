from core.models import Block, BlockTask


def sync_blocktasks(user, items):
    blocks_map = {b.uuid: b for b in Block.objects.filter(owner=user)}

    existing = {t.uuid: t for t in BlockTask.objects.filter(block__owner=user)}

    for data in items:
        uuid = data["uuid"]
        block_uuid = data["block_uuid"]

        block = blocks_map.get(block_uuid)
        if not block:
            continue

        obj = existing.get(uuid)

        if obj:
            obj.title = data.get("title", obj.title)
            obj.description = data.get("description", obj.description)
            obj.position = data.get("position", obj.position)
            obj.amount = data.get("amount", obj.amount)
            obj.time = data.get("time", obj.time)
            obj.icon = data.get("icon", obj.icon)
            obj.template = data.get("template_uuid", obj.template)
            obj.is_hidden = data.get("is_hidden", obj.is_hidden)
            obj.is_encrypted = data.get("is_encrypted", obj.is_encrypted)
            obj.updated_at = data.get("updated_at", obj.updated_at)
            obj.save()

        else:
            BlockTask.objects.create(
                uuid=uuid,
                block=block,
                title=data.get("title", ""),
                description=data.get("description", ""),
                position=data.get("position", 0),
                amount=data.get("amount", 1),
                time=data.get("time", 1),
                icon=data.get("icon"),
                template_id=data.get("template_uuid"),
                is_hidden=data.get("is_hidden", False),
                is_encrypted=data.get("is_encrypted", False),
            )
