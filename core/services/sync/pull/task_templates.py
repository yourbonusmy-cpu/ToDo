from core.models import TaskTemplate
from core.utils.icons import resolve_icon


from django.conf import settings


def get_task_templates(request, last_sync):
    qs = TaskTemplate.objects.filter(owner=request.user)

    if last_sync:
        qs = qs.filter(updated_at__gt=last_sync)

    data = list(
        qs.values(
            "uuid",
            "system_template__uuid",
            "title",
            "icon",
            "description",
            "is_hidden",
            "default_amount",
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
                f"{settings.MEDIA_URL}{item['icon']}"
            )

    return data
