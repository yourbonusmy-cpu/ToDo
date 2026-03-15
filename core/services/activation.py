from datetime import date
from django.utils import timezone


def is_task_active(task_template):
    today = date.today()
    last = task_template.last_completed_at
    period = task_template.period_type
    schedule = task_template.schedule_type

    if period == "none" and schedule == "none":
        return last is None

    if period == "week":
        if last and last.isocalendar()[1] == today.isocalendar()[1]:
            return False
        if schedule == "fixed":
            return today.weekday() == task_template.fixed_weekday
        return True

    if period == "month":
        if last and last.month == today.month:
            return False
        if schedule == "fixed":
            return today.day == task_template.fixed_day_of_month
        return True

    if period == "year":
        if last and last.year == today.year:
            return False
        return (
            today.day == task_template.fixed_day_of_month
            and today.month == task_template.fixed_month_of_year
        )

    return False