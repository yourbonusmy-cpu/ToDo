import json
import shutil
from pathlib import Path

from django.conf import settings

from core.models import TaskTemplate


def load_default_templates_for_user(user):

    if TaskTemplate.objects.filter(owner=user).exists():
        return

    base_path = Path(settings.BASE_DIR) / "static" / "default_templates"

    json_file = base_path / "templates.json"
    icons_path = base_path / "icons"

    with open(json_file, "r", encoding="utf-8") as f:
        templates = json.load(f)

    user_icon_dir = Path(settings.MEDIA_ROOT) / "image" / user.username / "task_icons"

    user_icon_dir.mkdir(parents=True, exist_ok=True)

    for t in templates:

        icon_filename = t.get("icon")

        icon_dest = ""
        if icon_filename:

            src = icons_path / icon_filename
            dst = user_icon_dir / icon_filename

            if src.exists():
                shutil.copy(src, dst)

            icon_dest = f"image/{user.username}/task_icons/{icon_filename}"

        TaskTemplate.objects.create(
            owner=user,
            title=t["title"],
            description=t.get("description", ""),
            icon=icon_dest,
            default_amount=t.get("default_amount", 1),
            period_type=t.get("period_type", "none"),
            schedule_type=t.get("schedule_type", "none"),
            priority=t.get("priority", 0),
        )
