from django.utils.timezone import now

from .blocks import get_blocks
from .blocktasks import get_blocktasks
from .templates import get_templates
from .groups import get_group_templates
from .system_templates import get_system_templates
from .deleted import get_deleted


def build_pull_response(request, last_sync):
    return {
        "server_time": now(),
        "blocks": get_blocks(request, last_sync),
        "block_tasks": get_blocktasks(request, last_sync),
        "task_templates": get_templates(request, last_sync),
        "group_templates": get_group_templates(request, last_sync),
        "system_templates": get_system_templates(request, last_sync),
        "deleted": get_deleted(request, last_sync),
    }
