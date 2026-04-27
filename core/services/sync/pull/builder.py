from django.utils.timezone import now

from .blocks import get_blocks
from .blocktasks import get_blocktasks
from .templates import get_templates
from .groups import get_groups
from .system_templates import get_system_templates
from .deleted import get_deleted


def build_pull_response(user, last_sync):
    return {
        "server_time": now(),
        "blocks": get_blocks(user, last_sync),
        "tasks": get_blocktasks(user, last_sync),
        "templates": get_templates(user, last_sync),
        "groups": get_groups(user, last_sync),
        "system_templates": get_system_templates(last_sync),
        "deleted": get_deleted(user, last_sync),
    }
