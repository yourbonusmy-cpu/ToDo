from uuid import UUID

from core.models import Block, BlockTask, TaskTemplate
from core.services.sync.common.conflict import resolve_update
from core.services.sync.common.time import safe_parse_dt
from urllib.parse import urlparse


def sync_blocktasks(user, items):
    blocks_map = {b.uuid: b for b in Block.objects.filter(owner=user)}

    templates_map = {t.uuid: t for t in TaskTemplate.objects.filter(owner=user)}

    existing = {t.uuid: t for t in BlockTask.objects.filter(block__owner=user)}

    for data in items:
        uuid = UUID(data["uuid"])

        block_uuid = UUID(data["block_uuid"])
        block = blocks_map.get(block_uuid)

        if not block:
            print(f"[WARN] Block not found: {block_uuid}")
            continue

        client_created_at = safe_parse_dt(data.get("created_at"))

        client_updated_at = safe_parse_dt(data.get("updated_at"))

        # TEMPLATE
        template = None
        template_uuid = data.get("template_uuid")

        if template_uuid:
            try:
                template = templates_map.get(UUID(template_uuid))
            except Exception:
                print(f"[WARN] Invalid template_uuid: {template_uuid}")

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
            obj.description = data.get(
                "description",
                obj.description,
            )

            obj.position = data.get(
                "position",
                obj.position,
            )

            obj.amount = data.get(
                "amount",
                obj.amount,
            )

            obj.time = data.get(
                "time",
                obj.time,
            )

            obj.icon = normalize_icon_path(data.get("icon")) or obj.icon

            obj.template = template

            obj.is_hidden = data.get(
                "is_hidden",
                obj.is_hidden,
            )

            obj.is_encrypted = data.get(
                "is_encrypted",
                obj.is_encrypted,
            )

            if client_updated_at:
                obj.updated_at = client_updated_at

            obj.save()

        # CREATE
        else:
            BlockTask.objects.create(
                uuid=uuid,
                block=block,
                template=template,
                title=data.get("title", ""),
                description=data.get(
                    "description",
                    "",
                ),
                icon=normalize_icon_path(data.get("icon")),
                position=data.get("position", 0),
                amount=data.get("amount", 1),
                time=data.get("time", 1),
                is_hidden=data.get(
                    "is_hidden",
                    False,
                ),
                is_encrypted=data.get(
                    "is_encrypted",
                    False,
                ),
                created_at=client_created_at,
                updated_at=client_updated_at,
            )


def normalize_icon_path(icon: str | None) -> str | None:
    if not icon:
        return icon

    # если уже относительный путь — оставляем
    if not icon.startswith("http"):
        return icon

    parsed = urlparse(icon)

    path = parsed.path  # /media/image/test/task_icons/file.png

    # убираем /media/
    if path.startswith("/media/"):
        path = path[len("/media/") :]

    return path.lstrip("/")
