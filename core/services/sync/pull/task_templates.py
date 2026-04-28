from core.models import TaskTemplate


def get_task_templates(user, last_sync):
    qs = TaskTemplate.objects.filter(owner=user)

    if last_sync:
        qs = qs.filter(updated_at__gt=last_sync)

    return list(
        qs.values(
            "uuid",
            "system_template__uuid",
            "title",
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
