from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.models import TaskTemplate


@login_required
def stats_weekdays_page(request):
    system_tasks = TaskTemplate.objects.filter(owner=request.user).order_by("title")
    return render(
        request,
        "core/stats_weekdays.html",
        {
            "system_tasks": system_tasks,
        },
    )
