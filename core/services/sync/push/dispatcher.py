from django.db import transaction

from .delete import apply_deletions
from .templates_ import sync_templates
from .groups import sync_groups
from .blocks import sync_blocks
from .blocktasks import sync_blocktasks


def handle_push(user, payload, request):
    device_uuid = payload.get("device_uuid")

    with transaction.atomic():

        # 1. DELETE FIRST
        apply_deletions(user, device_uuid, payload.get("deleted", []))

        # 2. MASTER DATA
        sync_templates(
            request,
            user,
            payload.get("templates", []),
            request.FILES,
        )
        sync_groups(user, payload.get("group_templates", []))

        # 3. DOMAIN DATA
        sync_blocks(user, payload.get("blocks", []))
        sync_blocktasks(user, payload.get("tasks", []))
