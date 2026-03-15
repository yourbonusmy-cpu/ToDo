from datetime import timezone

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.db.models import Prefetch

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.models import Block, BlockTask, TaskTemplate

import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from core.crypto import encrypt_text


@require_POST
@login_required
def block_delete(request, block_id):

    block = Block.objects.get(id=block_id, owner=request.user)

    block.delete()

    return JsonResponse({"status": "ok"})


@login_required
@csrf_exempt
def hide_block(request, block_id):
    """
    Переключает состояние is_hided у блока
    """
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Only POST allowed"}, status=405
        )

    block = get_object_or_404(Block, id=block_id, owner=request.user)
    block.is_hided = not block.is_hided
    block.save()
    return JsonResponse({"status": "ok", "is_hided": block.is_hided})


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
@csrf_protect
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

    block_tasks = []

    for position, task in enumerate(tasks_data):

        template_id = task.get("id")
        if not template_id:
            continue

        template = TaskTemplate.objects.filter(
            id=int(template_id), owner=request.user
        ).first()

        if not template:
            continue

        description = task.get("description", template.description or "")

        is_encrypted = task.get("is_encrypted", False)
        print(f"is_encrypted: {is_encrypted} | description: {description}")
        # 🔐 ШИФРОВАНИЕ НА СЕРВЕРЕ
        if is_encrypted and description:
            # пароль должен приходить в запросе
            password = task.get("password")

            if not password:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Password required for encrypted task",
                    },
                    status=400,
                )

            description = encrypt_text(description, password)

        block_tasks.append(
            BlockTask(
                block=block,
                title=template.title,
                icon=template.icon.url if template.icon else "",
                amount=task.get("amount", template.default_amount),
                time=task.get("time", 1),
                description=description,
                is_encrypted=is_encrypted,
                position=position,
            )
        )

    if block_tasks:
        BlockTask.objects.bulk_create(block_tasks)

    return JsonResponse({"status": "ok", "block_id": block.id})


@login_required
def create_block_old(request):
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
                    title=template.title,
                    icon=template.icon.url if template.icon else "",
                    amount=task.get("amount", template.default_amount),
                    time=task.get("time", 1),
                    description=task.get("description", template.description or ""),
                    position=position,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )
            )

        BlockTask.objects.bulk_create(block_tasks)

    return JsonResponse({"status": "ok", "block_id": block.id})


def load_blocks(request):

    page = request.GET.get("page", 1)

    blocks_qs = (
        Block.objects.filter(owner=request.user)
        .prefetch_related(
            Prefetch(
                "tasks",
                queryset=BlockTask.objects.order_by("position"),
            )
        )
        .order_by("-created_at")
    )

    paginator = Paginator(blocks_qs, 5)
    page_obj = paginator.get_page(page)

    html = ""

    for block in page_obj:
        html += render_to_string(
            "core/partials/block.html", {"block": block}, request=request
        )

    return JsonResponse(
        {
            "html": html,
            "has_next": page_obj.has_next(),
        }
    )


@login_required
@csrf_exempt
def update_block(request, block_id):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Only POST allowed"}, status=405
        )

    block = get_object_or_404(Block, id=block_id, owner=request.user)

    try:
        data = json.loads(request.body)
        block.title = data.get("title", block.title)
        tasks_data = data.get("tasks", [])
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

    block.save()

    # Существующие задачи блока
    existing_tasks = {str(bt.id): bt for bt in block.tasks.all()}  # ключ — id BlockTask
    used_ids = []
    new_tasks = []

    for position, task in enumerate(tasks_data):
        task_id = str(task.get("id"))

        if task_id in existing_tasks:
            # обновляем существующую задачу
            bt = existing_tasks[task_id]
            bt.title = task.get("title", bt.title)
            bt.description = task.get("description", bt.description)
            bt.amount = task.get("amount", bt.amount)
            bt.time = task.get("time", bt.time)
            bt.icon = task.get("icon", bt.icon)
            bt.position = position
            bt.save()
            used_ids.append(task_id)
        else:
            # создаём новую задачу
            new_tasks.append(
                BlockTask(
                    block=block,
                    title=task.get("title", "Новая задача"),
                    description=task.get("description", ""),
                    amount=task.get("amount", 1),
                    time=task.get("time", 1),
                    icon=task.get("icon", ""),
                    position=position,
                )
            )

    # удаляем задачи, которые больше не используются
    for task_id, bt in existing_tasks.items():
        if task_id not in used_ids:
            bt.delete()

    if new_tasks:
        BlockTask.objects.bulk_create(new_tasks)

    return JsonResponse({"status": "ok"})
