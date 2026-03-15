import json

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from core.crypto import encrypt_text
from core.models import Block, BlockTask, TaskTemplate, GroupTemplate

import json
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from core.models import Block, BlockTask, TaskTemplate


import json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required


from django.db.models import Prefetch


@login_required
@csrf_protect
def decrypt_task(request):

    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)

    data = json.loads(request.body)
    task_id = data.get("task_id")
    password = data.get("password")

    bt = get_object_or_404(BlockTask, id=task_id, block__owner=request.user)

    if not bt.is_encrypted:
        return JsonResponse({"status": "error", "message": "Task is not encrypted"})

    try:
        from core.crypto import decrypt_text

        decrypted = decrypt_text(bt.description, password)
    except Exception:
        return JsonResponse({"status": "error", "message": "Wrong password"})

    return JsonResponse({"status": "ok", "description": decrypted})


@login_required
def block_builder(request, block_id=None):

    templates = TaskTemplate.objects.filter(owner=request.user)

    groups = GroupTemplate.objects.filter(owner=request.user).prefetch_related(
        Prefetch("tasks", queryset=TaskTemplate.objects.only("id", "icon"))
    )

    block_data = None
    block = None

    if block_id:
        block = get_object_or_404(Block, id=block_id, owner=request.user)

        tasks = block.tasks.order_by("position")

        block_data = {
            "id": block.id,
            "title": block.title,
            "tasks": [
                {
                    "id": bt.id,
                    "title": bt.title,
                    "description": bt.description,
                    "amount": bt.amount,
                    "time": bt.time,
                    "icon": str(bt.icon) if bt.icon else "",
                    "is_encrypted": bt.is_encrypted,
                    "is_hidden": bt.is_hidden,  # 👈 ДОБАВЛЕНО
                }
                for bt in tasks
            ],
        }

    if request.method == "POST":

        if request.content_type == "application/json":
            body = json.loads(request.body)
            title = body.get("title", "Без названия")
            tasks_list = body.get("tasks", [])
        else:
            title = request.POST.get("title", "Без названия")
            tasks_json = request.POST.get("tasks", "[]")
            tasks_list = json.loads(tasks_json)

        # ==========================
        # UPDATE EXISTING BLOCK
        # ==========================

        if block:

            block.title = title
            block.save()

            existing_tasks = {t.id: t for t in block.tasks.all()}
            incoming_ids = set()

            for idx, task_data in enumerate(tasks_list):

                task_id = task_data.get("id")

                description = task_data.get("description", "")
                is_encrypted = task_data.get("is_encrypted", False)
                is_hidden = task_data.get("is_hidden", False)  # 👈 ДОБАВЛЕНО

                # 🔐 Server-side encryption
                if is_encrypted:
                    password = task_data.get("password")
                    if password:
                        description = encrypt_text(description, password)

                if task_id and task_id in existing_tasks:

                    bt = existing_tasks[task_id]

                    bt.title = task_data.get("title", bt.title)
                    bt.description = description
                    bt.amount = task_data.get("amount", bt.amount)
                    bt.time = task_data.get("time", bt.time)
                    bt.icon = task_data.get("icon", bt.icon)
                    bt.is_encrypted = is_encrypted
                    bt.is_hidden = is_hidden  # 👈 ДОБАВЛЕНО
                    bt.position = idx

                    bt.save()

                else:

                    bt = BlockTask.objects.create(
                        block=block,
                        title=task_data.get("title"),
                        description=description,
                        amount=task_data.get("amount", 0),
                        time=task_data.get("time", 0),
                        icon=task_data.get("icon", ""),
                        is_encrypted=is_encrypted,
                        is_hidden=is_hidden,  # 👈 ДОБАВЛЕНО
                        position=idx,
                    )

                incoming_ids.add(bt.id)

            # удаление отсутствующих задач
            to_delete = set(existing_tasks.keys()) - incoming_ids
            if to_delete:
                BlockTask.objects.filter(id__in=to_delete).delete()

        # ==========================
        # CREATE NEW BLOCK
        # ==========================

        else:

            block = Block.objects.create(title=title, owner=request.user)

            for idx, task_data in enumerate(tasks_list):

                description = task_data.get("description", "")
                is_encrypted = task_data.get("is_encrypted", False)
                is_hidden = task_data.get("is_hidden", False)  # 👈 ДОБАВЛЕНО

                # 🔐 Server-side encryption
                if is_encrypted:
                    password = task_data.get("password")
                    if password:
                        description = encrypt_text(description, password)

                BlockTask.objects.create(
                    block=block,
                    title=task_data.get("title"),
                    description=description,
                    amount=task_data.get("amount", 0),
                    time=task_data.get("time", 0),
                    icon=task_data.get("icon", ""),
                    is_encrypted=is_encrypted,
                    is_hidden=is_hidden,  # 👈 ДОБАВЛЕНО
                    position=idx,
                )

        return redirect("/")

    return render(
        request,
        "core/block_builder.html",
        {
            "templates": templates,
            "groups": groups,
            "block_json": json.dumps(block_data) if block_data else "null",
        },
    )


@login_required
def block_builder_old_2(request, block_id=None):

    templates = TaskTemplate.objects.filter(owner=request.user)

    # 🔹 ДОБАВИТЬ ЭТО
    groups = GroupTemplate.objects.filter(owner=request.user).prefetch_related(
        Prefetch("tasks", queryset=TaskTemplate.objects.only("id", "icon"))
    )

    block_data = None
    block = None

    if block_id:
        block = get_object_or_404(Block, id=block_id, owner=request.user)
        tasks = block.tasks.order_by("position")

        block_data = {
            "id": block.id,
            "title": block.title,
            "tasks": [
                {
                    "id": bt.id,
                    "title": bt.title,
                    "description": bt.description,
                    "amount": bt.amount,
                    "time": bt.time,
                    "icon": str(bt.icon) if bt.icon else "",
                }
                for bt in tasks
            ],
        }

    if request.method == "POST":

        if request.content_type == "application/json":
            body = json.loads(request.body)
            title = body.get("title", "Без названия")
            tasks_list = body.get("tasks", [])
        else:
            title = request.POST.get("title", "Без названия")
            tasks_json = request.POST.get("tasks", "[]")
            tasks_list = json.loads(tasks_json)

        if block:
            block.title = title
            block.save()

            existing_task_ids = set(block.tasks.values_list("id", flat=True))
            incoming_task_ids = set()

            for idx, task_data in enumerate(tasks_list):

                task_id = task_data.get("id")

                if (
                    task_id
                    and isinstance(task_id, int)
                    and task_id in existing_task_ids
                ):

                    bt = BlockTask.objects.get(id=task_id)

                    bt.title = task_data.get("title", bt.title)
                    description = task_data.get("description", bt.description)
                    is_encrypted = task_data.get("is_encrypted", bt.is_encrypted)

                    if is_encrypted:

                        password = task_data.get("password")

                        if password:
                            description = encrypt_text(description, password)

                    bt.description = description
                    bt.is_encrypted = is_encrypted
                    bt.amount = task_data.get("amount", bt.amount)
                    bt.time = task_data.get("time", bt.time)
                    bt.icon = task_data.get("icon", bt.icon)
                    bt.position = idx

                    bt.save()

                else:

                    bt = BlockTask.objects.create(
                        block=block,
                        title=task_data.get("title"),
                        description=description,
                        is_encrypted=is_encrypted,
                        amount=task_data.get("amount", 0),
                        time=task_data.get("time", ""),
                        icon=task_data.get("icon", ""),
                        position=idx,
                    )

                incoming_task_ids.add(bt.id)

            to_delete = existing_task_ids - incoming_task_ids
            if to_delete:
                BlockTask.objects.filter(id__in=to_delete).delete()

        else:

            block = Block.objects.create(title=title, owner=request.user)

            for idx, task_data in enumerate(tasks_list):

                BlockTask.objects.create(
                    block=block,
                    title=task_data.get("title"),
                    description=task_data.get("description", ""),
                    amount=task_data.get("amount", 0),
                    time=task_data.get("time", ""),
                    icon=task_data.get("icon", ""),
                    position=idx,
                )

        return redirect("/")

    return render(
        request,
        "core/block_builder.html",
        {
            "templates": templates,
            "groups": groups,  # 🔹 ДОБАВИЛИ
            "block_json": json.dumps(block_data) if block_data else "null",
        },
    )


@login_required
def create_block(request):
    """
    Создание нового блока
    """
    data = json.loads(request.body)
    title = data.get("title", "Новый блок")
    tasks_data = data.get("tasks", [])

    block = Block.objects.create(owner=request.user, title=title)

    block_tasks = []
    for position, task in enumerate(tasks_data):
        template = TaskTemplate.objects.get(id=task["id"])
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
    return JsonResponse({"status": "ok"})


@login_required
@csrf_exempt
def delete_block(request, block_id):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Only POST allowed"}, status=405
        )

    block = get_object_or_404(Block, id=block_id, owner=request.user)
    block.delete()
    return JsonResponse({"status": "ok"})


@login_required
def update_block(request, block_id):
    """
    Обновление существующего блока
    """
    block = get_object_or_404(Block, id=block_id, owner=request.user)
    data = json.loads(request.body)
    title = data.get("title", block.title)
    tasks_data = data.get("tasks", [])

    block.title = title
    block.save()

    # Собираем текущие BlockTask
    existing_tasks = {bt.template.id: bt for bt in block.blocktask_set.all()}

    new_tasks = []
    used_template_ids = []

    for position, task in enumerate(tasks_data):
        template_id = task["id"]
        used_template_ids.append(template_id)
        if template_id in existing_tasks:
            # обновляем
            bt = existing_tasks[template_id]
            bt.amount = task.get("amount", bt.amount)
            bt.time = task.get("time", bt.time)
            bt.description = task.get("description", bt.description)
            bt.position = position
            bt.save()
        else:
            # новая задача
            template = TaskTemplate.objects.get(id=template_id)
            new_tasks.append(
                BlockTask(
                    block=block,
                    template=template,
                    amount=task.get("amount", 1),
                    time=task.get("time", 1),
                    description=task.get("description", ""),
                    position=position,
                )
            )

    # удалить ненужные
    for template_id, bt in existing_tasks.items():
        if template_id not in used_template_ids:
            bt.delete()

    if new_tasks:
        BlockTask.objects.bulk_create(new_tasks)

    return JsonResponse({"status": "ok"})
