from django.utils.timezone import now

from .block_tasks import get_block_tasks
from .blocks import get_blocks
from .group_templates import get_group_templates
from .system_templates import get_system_templates
from .deleted import get_deleted
from .task_templates import get_task_templates


def build_pull_response(user, last_sync):
    return {
        "server_time": now(),
        "blocks": get_blocks(user, last_sync),
        "block_tasks": get_block_tasks(user, last_sync),
        "task_templates": get_task_templates(user, last_sync),
        "group_templates": get_group_templates(user, last_sync),
        "system_templates": get_system_templates(last_sync),
        "deleted": get_deleted(user, last_sync),
    }
