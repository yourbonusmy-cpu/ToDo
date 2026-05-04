from config import settings
from core.models import SystemTaskTemplate


def get_system_templates(request, last_sync):
    qs = SystemTaskTemplate.objects.all()

    if last_sync:
        qs = qs.filter(updated_at__gt=last_sync)

    data = list(
        qs.values(
            "uuid",
            "code",
            "title",
            "description",
            "is_hidden",
            "icon",
            "amount",
            "period_type",
            "schedule_type",
            "fixed_weekday",
            "fixed_day_of_month",
            "fixed_month_of_year",
            "priority",
            "updated_at",
            "created_at",
        )
    )

    for item in data:
        icon_name = item.get("icon")

        if icon_name and icon_name.strip():
            icon_path = f"static/default_templates/icons/{icon_name.lstrip('/')}"
            item["icon"] = request.build_absolute_uri(f"/{icon_path}")
        else:
            item["icon"] = None

    return data
