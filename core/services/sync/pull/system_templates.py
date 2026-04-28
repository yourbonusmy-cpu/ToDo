from config import settings
from core.models import SystemTaskTemplate


def get_system_templates(last_sync):
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
            "default_amount",
            "period_type",
            "schedule_type",
            "fixed_weekday",
            "fixed_day_of_month",
            "fixed_month_of_year",
            "priority",
            "updated_at",
        )
    )

    return data
