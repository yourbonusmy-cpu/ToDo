from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay

from core.models import BlockTask

# Django weekday → человеко-понятный
WEEKDAYS = {
    2: "Пн",
    3: "Вт",
    4: "Ср",
    5: "Чт",
    6: "Пт",
    7: "Сб",
    1: "Вс",
}


@login_required
def stats_weekdays_api(request):
    """
    Статистика по дням недели:
    - фильтр по минимальному количеству
    - исключение выбранных задач
    """

    # ---------------------------
    # PARAMS
    # ---------------------------
    try:
        min_count = int(request.GET.get("min", 3))
    except ValueError:
        min_count = 3

    exclude_tasks = request.GET.getlist("exclude_tasks")

    # ---------------------------
    # QUERY
    # ---------------------------
    qs = BlockTask.objects.filter(
        block__owner=request.user,
        block__target_date__isnull=False,
        is_hidden=False,
        template__isnull=False,
    )

    if exclude_tasks:
        qs = qs.exclude(template__id__in=exclude_tasks)

    qs = (
        qs.annotate(weekday=ExtractWeekDay("block__target_date"))
        .values(
            "weekday",
            "template__id",
            "template__title",
            "template__icon",
        )
        .annotate(cnt=Count("id"))
        .order_by()
    )

    # ---------------------------
    # BUILD RESULT
    # ---------------------------
    result = {k: [] for k in WEEKDAYS.keys()}

    for row in qs:
        if row["cnt"] < min_count:
            continue

        result[row["weekday"]].append(
            {
                "template_id": row["template__id"],
                "title": row["template__title"],
                "icon": str(row["template__icon"]) if row["template__icon"] else "",
                "count": row["cnt"],
            }
        )

    # ---------------------------
    # SORT
    # ---------------------------
    for day in result:
        result[day].sort(key=lambda x: -x["count"])

    return JsonResponse(
        {
            "weekdays": WEEKDAYS,
            "data": result,
        }
    )
