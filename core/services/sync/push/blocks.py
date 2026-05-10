from uuid import UUID

from core.models import Block
from core.services.sync.common.conflict import resolve_update
from core.services.sync.common.time import safe_parse_dt
from core.services.sync.common.uuid import as_uuid_map


def sync_blocks(user, items):
    existing = as_uuid_map(Block.objects.filter(owner=user))

    for data in items:
        uuid = UUID(data["uuid"])

        client_created_at = safe_parse_dt(data.get("created_at"))

        client_updated_at = safe_parse_dt(data.get("updated_at"))

        obj = existing.get(uuid)

        # UPDATE
        if obj:
            if not resolve_update(
                obj,
                data,
                client_updated_at,
                obj.updated_at,
            ):
                continue

            obj.title = data.get("title", obj.title)
            obj.priority = data.get("priority", obj.priority)
            obj.is_hidden = data.get("is_hidden", obj.is_hidden)
            obj.target_date = data.get(
                "target_date",
                obj.target_date,
            )

            # ВАЖНО:
            # updated_at теперь берем с клиента
            if client_updated_at:
                obj.updated_at = client_updated_at

            obj.save()

        # CREATE
        else:
            Block.objects.create(
                owner=user,
                uuid=uuid,
                title=data.get("title", ""),
                priority=data.get("priority", 0),
                is_hidden=data.get("is_hidden", False),
                target_date=data.get("target_date"),
                # ВАЖНО:
                # сохраняем клиентские даты
                created_at=client_created_at,
                updated_at=client_updated_at,
            )
