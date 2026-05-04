from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from core.models import TaskTemplate, Block


def calendar_page(request):
    if not request.user.is_authenticated:
        return render(request, "core/landing.html")

    task_templates = TaskTemplate.objects.filter(owner=request.user).order_by("title")

    return render(
        request,
        "core/blocks/calendar.html",
        {
            "system_tasks": task_templates,
        },
    )


@login_required
def calendar_data(request):
    year = int(request.GET.get("year"))
    month = int(request.GET.get("month"))

    blocks = Block.objects.filter(
        owner=request.user,
        is_hidden=False,
        target_date__isnull=False,
        target_date__year=year,
        target_date__month=month,
    ).prefetch_related("block_tasks")

    result = {}

    for block in blocks:
        date = block.target_date.isoformat()

        tasks = [
            {
                "id": t.template.pk,
                "title": t.title,
                "icon": t.icon,
            }
            for t in block.block_tasks.filter(is_hidden=False)
        ]

        if date not in result:
            result[date] = []

        result[date].append(
            {
                "id": block.pk,
                "title": block.title,
                "tasks_count": len(tasks),
                "tasks": tasks,
            }
        )

    return JsonResponse(result)
