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
    Возвращает статистику по дням недели:
    - сколько раз шаблон встречается в конкретный день
    - фильтр по минимальному количеству
    - фильтр "убрать ежедневные"
    """

    # ---------------------------
    # PARAMS
    # ---------------------------
    try:
        min_count = int(request.GET.get("min", 3))
    except ValueError:
        min_count = 3

    exclude_daily = request.GET.get("exclude_daily") == "1"

    # ---------------------------
    # QUERY
    # ---------------------------
    qs = (
        BlockTask.objects.filter(
            block__owner=request.user,
            block__target_date__isnull=False,
            is_hidden=False,
            template__isnull=False,  # важно
        )
        .annotate(weekday=ExtractWeekDay("block__target_date"))
        .values(
            "weekday",
            "template__id",
            "template__title",
            "template__icon",
        )
        .annotate(cnt=Count("id"))
        .order_by()  # сбрасываем дефолтную сортировку
    )

    # ---------------------------
    # DAYS PER TEMPLATE
    # ---------------------------
    template_days = defaultdict(set)

    for row in qs:
        template_days[row["template__id"]].add(row["weekday"])

    # ---------------------------
    # BUILD RESULT
    # ---------------------------
    result = {k: [] for k in WEEKDAYS.keys()}

    for row in qs:
        template_id = row["template__id"]
        weekday = row["weekday"]
        count = row["cnt"]

        # фильтр по количеству
        if count < min_count:
            continue

        # фильтр "ежедневные"
        if exclude_daily and len(template_days[template_id]) >= 5:
            continue

        result[weekday].append(
            {
                "template_id": template_id,
                "title": row["template__title"],
                "icon": str(row["template__icon"]) if row["template__icon"] else "",
                "count": count,
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
