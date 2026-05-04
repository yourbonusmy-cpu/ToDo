from config import settings
from core.models import TaskTemplate


def get_templates(request, last_sync):
    qs = TaskTemplate.objects.filter(owner=request.user)

    if last_sync:
        qs = qs.filter(updated_at__gt=last_sync)

    data = list(
        qs.values(
            "uuid",
            "system_template__uuid",
            "title",
            "description",
            "icon",
            "is_hidden",
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
        if item["icon"]:
            item["icon"] = request.build_absolute_uri(
                settings.MEDIA_URL + item["icon"].lstrip("/")
            )
        else:
            item["icon"] = None

    return data
