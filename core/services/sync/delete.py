from django.db import transaction

from core.models import (
    Block,
    BlockTask,
    TaskTemplate,
    GroupTemplate,
    SystemTaskTemplate,
    DeletedObject,
)

OBJECT_MAP = {
    "block": Block,
    "blocktask": BlockTask,
    "template": TaskTemplate,
    "group": GroupTemplate,
    "system_template": SystemTaskTemplate,
}


def apply_deletions(user, device_id, deleted_list):
    """
    deleted_list format:
    [
        {"uuid": "...", "type": "block"},
        {"uuid": "...", "type": "blocktask"},
    ]
    """

    if not deleted_list:
        return

    # batch check already applied deletions
    incoming_keys = set((i["uuid"], i["type"]) for i in deleted_list)

    existing = set(
        DeletedObject.objects.filter(
            user=user,
            obj_uuid__in=[i["uuid"] for i in deleted_list],
        ).values_list("obj_uuid", "object_type")
    )

    to_create = []
    to_delete_queries = {
        "block": [],
        "blocktask": [],
        "template": [],
        "group": [],
        "system_template": [],
    }

    for item in deleted_list:
        uuid = item["uuid"]
        obj_type = item["type"]

        # idempotency (важно для multi-device sync)
        if (uuid, obj_type) in existing:
            continue

        to_create.append(
            DeletedObject(
                obj_uuid=uuid,
                object_type=obj_type,
                user=user,
                device_id=device_id,
            )
        )

        model = OBJECT_MAP.get(obj_type)
        if model:
            to_delete_queries[obj_type].append(uuid)

    # -------------------------
    # BULK INSERT TOMBSTONES
    # -------------------------
    if to_create:
        DeletedObject.objects.bulk_create(to_create, ignore_conflicts=True)

    # -------------------------
    # HARD DELETE (LOCAL STATE)
    # -------------------------
    if to_delete_queries["block"]:
        Block.objects.filter(owner=user, uuid__in=to_delete_queries["block"]).delete()

    if to_delete_queries["blocktask"]:
        BlockTask.objects.filter(uuid__in=to_delete_queries["blocktask"]).delete()

    if to_delete_queries["template"]:
        TaskTemplate.objects.filter(
            owner=user, uuid__in=to_delete_queries["template"]
        ).delete()

    if to_delete_queries["group"]:
        GroupTemplate.objects.filter(
            owner=user, uuid__in=to_delete_queries["group"]
        ).delete()

    if to_delete_queries["system_template"]:
        SystemTaskTemplate.objects.filter(
            uuid__in=to_delete_queries["system_template"]
        ).delete()
