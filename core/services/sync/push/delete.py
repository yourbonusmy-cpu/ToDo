from core.models import (
    Block,
    BlockTask,
    TaskTemplate,
    GroupTemplate,
    DeletedObject,
)

OBJECT_MAP = {
    "block": Block,
    "blocktask": BlockTask,
    "template": TaskTemplate,
    "group": GroupTemplate,
}


def apply_deletions(user, device_uuid, deleted_list):
    if not deleted_list:
        return

    to_create = []

    for item in deleted_list:
        uuid = item["uuid"]
        obj_type = item["type"]

        # idempotency (защита от повторного push)
        exists = DeletedObject.objects.filter(
            obj_uuid=uuid, object_type=obj_type, user=user
        ).exists()

        if exists:
            continue

        to_create.append(
            DeletedObject(
                obj_uuid=uuid,
                object_type=obj_type,
                user=user,
                device_uuid=device_uuid,
            )
        )

        model = OBJECT_MAP.get(obj_type)

        if model is Block:
            Block.objects.filter(owner=user, uuid=uuid).delete()

        elif model is BlockTask:
            BlockTask.objects.filter(uuid=uuid).delete()

        elif model is TaskTemplate:
            TaskTemplate.objects.filter(owner=user, uuid=uuid).delete()

        elif model is GroupTemplate:
            GroupTemplate.objects.filter(owner=user, uuid=uuid).delete()

    if to_create:
        DeletedObject.objects.bulk_create(to_create, ignore_conflicts=True)
