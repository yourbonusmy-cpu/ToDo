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
            obj.is_hidden = data.get("is_hidden", obj.is_hidden)
            obj.save()

        else:
            BlockTask.objects.create(
                uuid=uuid,
                block=block,
                title=data.get("title", ""),
                position=data.get("position", 0),
            )
