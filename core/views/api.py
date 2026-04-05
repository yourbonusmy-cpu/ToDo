from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from core.models import Block, BlockTask, TaskTemplate

# core/views/api.py

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime
from datetime import datetime

from core.models import Block


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
    ).prefetch_related("tasks")

    result = {}

    for block in blocks:
        date = block.target_date.isoformat()

        tasks = [
            {
                "title": t.title,
                "icon": t.icon,
            }
            for t in block.tasks.filter(is_hidden=False)
        ]

        if date not in result:
            result[date] = []

        result[date].append(
            {
                "id": block.id,
                "title": block.title,
                "tasks_count": len(tasks),
                "tasks": tasks,
            }
        )

    return JsonResponse(result)


@login_required
def get_block(request, block_id):

    block = get_object_or_404(Block, id=block_id, owner=request.user)

    tasks = block.tasks.select_related("template").order_by("position")

    data = {
        "id": block.id,
        "title": block.title,
        "tasks": [
            {
                "id": bt.template.id,
                "title": bt.template.title,
                "description": bt.description or bt.template.description,
                "amount": bt.amount,
                "time": bt.time,
                "icon": bt.template.icon.url if bt.template.icon else "",
            }
            for bt in tasks
        ],
    }

    return JsonResponse(data)


@login_required
@csrf_exempt
def create_block(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Only POST allowed"}, status=405
        )

    try:
        data = json.loads(request.body)
        title = data.get("title", "Новый блок")
        tasks_data = data.get("tasks", [])
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

    # создаём блок
    block = Block.objects.create(owner=request.user, title=title)

    # создаём задачи блока
    block_tasks = []
    if tasks_data:
        template_ids = [int(t["id"]) for t in tasks_data]
        templates = TaskTemplate.objects.in_bulk(template_ids)

        for position, task in enumerate(tasks_data):
            template = templates.get(int(task["id"]))
            if not template:
                continue

            block_tasks.append(
                BlockTask(
                    block=block,
                    template=template,
                    amount=task.get("amount", 1),
                    time=task.get("time", 1),
                    description=task.get("description", ""),
                    position=position,
                )
            )

        BlockTask.objects.bulk_create(block_tasks)

    return JsonResponse({"status": "ok", "block_id": block.id})


@login_required
def update_block(request, block_id):
    print("block id: ", block_id)
    block = get_object_or_404(Block, id=block_id, owner=request.user)

    data = json.loads(request.body)

    block.title = data.get("title", block.title)
    tasks_data = data.get("tasks", [])

    block.save()

    existing = {bt.template_id: bt for bt in block.tasks.all()}
    used_ids = []

    new_tasks = []

    for position, task in enumerate(tasks_data):

        template_id = task["id"]
        used_ids.append(template_id)

        if template_id in existing:

            bt = existing[template_id]

            bt.amount = task.get("amount", bt.amount)
            bt.time = task.get("time", bt.time)
            bt.description = task.get("description", bt.description)
            bt.position = position

            bt.save()

        else:

            template = TaskTemplate.objects.get(id=template_id)

            new_tasks.append(
                BlockTask(
                    block=block,
                    template=template,
                    template_title=template.title,
                    template_icon=template.icon.url if template.icon else "",
                    amount=task.get("amount", 1),
                    time=task.get("time", 1),
                    description=task.get("description", ""),
                    position=position,
                )
            )

    for template_id, bt in existing.items():
        if template_id not in used_ids:
            bt.delete()

    if new_tasks:
        BlockTask.objects.bulk_create(new_tasks)

    return JsonResponse({"status": "ok"})
