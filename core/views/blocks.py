import json
from datetime import datetime

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from core.crypto import encrypt_text
from core.models import (
    Block,
    BlockTask,
    TaskTemplate,
    GroupTemplate,
    PeriodType,
    ScheduleType,
    BlockWeather,
)

import json
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from core.models import Block, BlockTask, TaskTemplate


import json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required


from django.db.models import Prefetch, Q


from core.crypto import decrypt_text
from django.contrib.auth.hashers import check_password
from django.views.decorators.http import require_POST

from core.services.weather import (
    get_forecast,
    group_by_period,
    build_weather_cards,
    get_wind_direction,
    normalize_weather,
    get_weather_ui,
)


@login_required
@csrf_protect
def decrypt_task(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Method not allowed"}, status=405
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    task_id = data.get("task_id")
    password = data.get("password")
    if not task_id:
        return JsonResponse(
            {"status": "error", "message": "task_id and password required"}, status=400
        )

    bt = get_object_or_404(BlockTask, id=task_id, block__owner=request.user)

    if not bt.is_encrypted:
        return JsonResponse(
            {"status": "error", "message": "Task is not encrypted"}, status=400
        )

    decrypted = decrypt_text(bt.description, password)

    if decrypted is None:
        return JsonResponse(
            {"status": "error", "message": "Wrong password"}, status=403
        )

    return JsonResponse({"status": "ok", "description": decrypted})


@login_required
def block_create(request, block_id=None):
    # ==========================
    # LOAD TEMPLATES
    # ==========================
    templates = TaskTemplate.objects.filter(owner=request.user)

    period_type = request.GET.get("period_type", PeriodType.NONE)
    schedule_type = request.GET.get("schedule_type", ScheduleType.NONE)

    if period_type != PeriodType.NONE:
        templates = templates.filter(period_type=period_type)
    if schedule_type != ScheduleType.NONE:
        templates = templates.filter(schedule_type=schedule_type)

    sorted_templates = templates.annotate(
        is_floating=(
            Q(schedule_type=ScheduleType.FLOATING)
            & Q(period_type__in=[PeriodType.WEEK, PeriodType.MONTH, PeriodType.YEAR])
        ),
        is_fixed=(
            Q(schedule_type=ScheduleType.FIXED)
            & Q(period_type__in=[PeriodType.WEEK, PeriodType.MONTH, PeriodType.YEAR])
        ),
    ).order_by(
        "-is_floating",
        "-fixed_weekday",
        "-fixed_day_of_month",
        "-fixed_month_of_year",
        "-next_available_at",
        "-selected_count",
        "-priority",
        "-last_used_at",
    )

    groups = GroupTemplate.objects.filter(owner=request.user).prefetch_related(
        Prefetch("tasks", queryset=TaskTemplate.objects.only("id", "icon"))
    )

    # ==========================
    # LOAD BLOCK (edit mode)
    # ==========================
    block = None
    block_data = None

    if block_id:
        block = get_object_or_404(Block, id=block_id, owner=request.user)
        tasks = block.tasks.order_by("position")

        block_data = {
            "id": block.id,
            "title": block.title,
            "weather": (
                getattr(block.weather, "data", None)
                if hasattr(block, "weather")
                else None
            ),
            "weather_city": (
                getattr(block.weather, "city", None)
                if hasattr(block, "weather")
                else None
            ),
            "target_date": block.target_date.isoformat() if block.target_date else None,
            "tasks": [
                {
                    "id": bt.id,
                    "title": bt.title,
                    "description": bt.description,
                    "amount": bt.amount,
                    "time": bt.time,
                    "icon": str(bt.icon) if bt.icon else "",
                    "is_encrypted": bt.is_encrypted,
                    "is_hidden": bt.is_hidden,
                    "template_id": bt.template.id if bt.template else None,
                }
                for bt in tasks
            ],
        }

    # ==========================
    # POST HANDLER
    # ==========================
    if request.method == "POST":

        # ---------- JSON ----------
        if request.content_type == "application/json":
            body = json.loads(request.body)

            title = body.get("title", "Без названия")
            target_date = body.get("target_date")
            tasks_list = body.get("tasks", [])

            with_weather = body.get("with_weather", False)
            city = body.get("weather_city", "Москва")
            weather_data_raw = body.get("weather_data")

        # ---------- FORM ----------
        else:
            title = request.POST.get("title", "Без названия")
            target_date = request.POST.get("target_date") or None

            tasks_json = request.POST.get("tasks", "[]")
            tasks_list = json.loads(tasks_json)

            with_weather = request.POST.get("with_weather") == "true"
            city = request.POST.get("weather_city", "Москва")
            weather_data_raw = request.POST.get("weather_data")

        # parse date safely
        if target_date:
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

        # ==========================
        # UPDATE BLOCK
        # ==========================
        if block:
            block.title = title
            block.target_date = target_date
            block.save()

            # ---------- WEATHER ----------
            if with_weather and weather_data_raw:
                try:
                    BlockWeather.objects.update_or_create(
                        block=block,
                        defaults={
                            "city": city,
                            "data": json.loads(weather_data_raw),
                        },
                    )
                except json.JSONDecodeError:
                    pass  # можно логировать

            elif not with_weather:
                BlockWeather.objects.filter(block=block).delete()

            # ---------- TASKS ----------
            existing_tasks = {t.id: t for t in block.tasks.all()}
            incoming_ids = set()

            for idx, task_data in enumerate(tasks_list):

                template_id = task_data.get("template_id")
                if not template_id:
                    raise ValueError("Каждая задача должна иметь template_id")

                template = get_object_or_404(
                    TaskTemplate, id=template_id, owner=request.user
                )

                task_id = task_data.get("id")
                description = task_data.get("description", "")
                is_encrypted = task_data.get("is_encrypted", False)
                is_hidden = task_data.get("is_hidden", False)

                # encryption
                if is_encrypted:
                    password = task_data.get("password")
                    decrypted = task_data.get("decrypted")

                    if decrypted and password:
                        description = encrypt_text(description, password)
                    elif task_id in existing_tasks:
                        description = existing_tasks[task_id].description

                if task_id and task_id in existing_tasks:
                    bt = existing_tasks[task_id]
                    bt.title = task_data.get("title", bt.title)
                    bt.description = description
                    bt.amount = task_data.get("amount", bt.amount)
                    bt.time = task_data.get("time", bt.time)
                    bt.icon = task_data.get("icon", bt.icon)
                    bt.is_encrypted = is_encrypted
                    bt.is_hidden = is_hidden
                    bt.template = template
                    bt.position = idx
                    bt.save()
                else:
                    bt = BlockTask.objects.create(
                        block=block,
                        template=template,
                        title=task_data.get("title"),
                        description=description,
                        amount=task_data.get("amount", 0),
                        time=task_data.get("time", 0),
                        icon=task_data.get("icon", ""),
                        is_encrypted=is_encrypted,
                        is_hidden=is_hidden,
                        position=idx,
                    )

                incoming_ids.add(bt.id)

            # delete removed tasks
            BlockTask.objects.filter(
                id__in=set(existing_tasks.keys()) - incoming_ids
            ).delete()

        # ==========================
        # CREATE BLOCK
        # ==========================
        else:
            block = Block.objects.create(
                title=title,
                owner=request.user,
                target_date=target_date,
            )

            for idx, task_data in enumerate(tasks_list):

                template_id = task_data.get("template_id")
                if not template_id:
                    raise ValueError("Каждая задача должна иметь template_id")

                template = get_object_or_404(
                    TaskTemplate, id=template_id, owner=request.user
                )

                description = task_data.get("description", "")
                is_encrypted = task_data.get("is_encrypted", False)
                is_hidden = task_data.get("is_hidden", False)

                if is_encrypted:
                    password = task_data.get("password")
                    if password:
                        description = encrypt_text(description, password)

                BlockTask.objects.create(
                    block=block,
                    template=template,
                    title=task_data.get("title"),
                    description=description,
                    amount=task_data.get("amount", 0),
                    time=task_data.get("time", 0),
                    icon=task_data.get("icon", ""),
                    is_encrypted=is_encrypted,
                    is_hidden=is_hidden,
                    position=idx,
                )

            # ---------- WEATHER ----------
            if with_weather and weather_data_raw:
                try:
                    BlockWeather.objects.create(
                        block=block,
                        city=city,
                        data=json.loads(weather_data_raw),
                    )
                except json.JSONDecodeError:
                    pass

        return redirect("/")

    # ==========================
    # RENDER
    # ==========================
    return render(
        request,
        "core/block_create.html",
        {
            "templates": sorted_templates,
            "groups": groups,
            "block_json": json.dumps(block_data) if block_data else "null",
            "MEDIA_URL": settings.MEDIA_URL,
        },
    )


@login_required
def block_builder__1803(request, block_id=None):
    # Получаем все шаблоны задач, принадлежащие пользователю
    templates = TaskTemplate.objects.filter(owner=request.user)

    # Фильтруем шаблоны задач по period_type и schedule_type
    period_type = request.GET.get("period_type", PeriodType.NONE)
    schedule_type = request.GET.get("schedule_type", ScheduleType.NONE)

    # Применяем фильтрацию по period_type и schedule_type
    if period_type != PeriodType.NONE:
        templates = templates.filter(period_type=period_type)

    if schedule_type != ScheduleType.NONE:
        templates = templates.filter(schedule_type=schedule_type)

    # ==========================
    # СОРТИРОВКА ЗАДАЧ ПО ПЕРИОДУ, ТИПУ РАСПИСАНИЯ И ДРУГИМ КРИТЕРИЯМ
    # ==========================
    sorted_templates = templates.annotate(
        # Аннотируем поля для сортировки
        is_floating=(
            Q(schedule_type=ScheduleType.FLOATING) & Q(period_type=PeriodType.WEEK)
        )
        | (Q(schedule_type=ScheduleType.FLOATING) & Q(period_type=PeriodType.MONTH))
        | (Q(schedule_type=ScheduleType.FLOATING) & Q(period_type=PeriodType.YEAR)),
        is_fixed=(Q(schedule_type=ScheduleType.FIXED) & Q(period_type=PeriodType.WEEK))
        | (Q(schedule_type=ScheduleType.FIXED) & Q(period_type=PeriodType.MONTH))
        | (Q(schedule_type=ScheduleType.FIXED) & Q(period_type=PeriodType.YEAR)),
    ).order_by(
        "-is_floating",  # Сначала плавающие задачи
        "-fixed_weekday",  # Для недельных задач
        "-fixed_day_of_month",  # Для месячных задач
        "-fixed_month_of_year",  # Для годовых задач
        "-next_available_at",  # Для задач с фиксированным временем
        "-selected_count",  # Сортировка по количеству выборов
        "-priority",  # Приоритет
        "-last_used_at",  # Последнее использование
    )

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
                    description_changed = task_data.get("description_changed")

                    if description_changed and password:
                        # пользователь расшифровал и изменил текст
                        description = encrypt_text(description, password)

                    else:
                        # описание не менялось → оставляем ciphertext
                        if task_id and task_id in existing_tasks:
                            description = existing_tasks[task_id].description

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
                    description_changed = task_data.get("description_changed")

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
                    is_hidden=is_hidden,
                    position=idx,
                )

        return redirect("/")

    return render(
        request,
        "core/block_create.html",
        {
            "templates": sorted_templates,
            "groups": groups,
            "block_json": json.dumps(block_data) if block_data else "null",
        },
    )


@login_required
def block_builder_stop(request, block_id=None):
    # Получаем фильтрованные шаблоны задач
    sorted_templates = get_filtered_templates(request)
    groups = GroupTemplate.objects.filter(owner=request.user).prefetch_related(
        Prefetch("tasks", queryset=TaskTemplate.objects.only("id", "icon"))
    )

    # Загрузка данных блока (если block_id передан)
    block, block_data = get_block_data(block_id, request.user)

    if request.method == "POST":
        # Обработка JSON или формы

        if request.content_type == "application/json":
            body = json.loads(request.body)
            title = body.get("title", "Без названия")
            tasks_list = body.get("tasks", [])
        else:
            title = request.POST.get("title", "Без названия")
            tasks_json = request.POST.get("tasks", "[]")
            tasks_list = json.loads(tasks_json)

        if block:
            update_block_data(block, tasks_list)
        else:
            create_new_block(title, tasks_list, request.user)

        return redirect("/")

    return render(
        request,
        "core/block_create.html",
        {
            "templates": sorted_templates,
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


def create_new_block(title, tasks_list, user):
    block = Block.objects.create(title=title, owner=user)

    for idx, task_data in enumerate(tasks_list):
        description = task_data.get("description", "")
        is_encrypted = task_data.get("is_encrypted", False)
        is_hidden = task_data.get("is_hidden", False)

        if is_encrypted:
            password = task_data.get("password")
            description = encrypt_text(description, password)

        BlockTask.objects.create(
            block=block,
            title=task_data.get("title"),
            description=description,
            amount=task_data.get("amount", 0),
            time=task_data.get("time", 0),
            icon=task_data.get("icon", ""),
            is_encrypted=is_encrypted,
            is_hidden=is_hidden,
            position=idx,
        )

    return block


@require_POST
@login_required
def delete_block(request, block_id):
    block = get_object_or_404(Block, id=block_id, owner=request.user)
    password = request.POST.get("password")
    if not password:
        return JsonResponse(
            {"status": "error", "message": "Password required"}, status=400
        )

    if not check_password(password, request.user.password):
        return JsonResponse(
            {"status": "error", "message": "Wrong password"}, status=403
        )

    block.delete()

    return JsonResponse({"status": "ok"})


def get_filtered_templates(request):
    templates = TaskTemplate.objects.filter(owner=request.user)

    period_type = request.GET.get("period_type", PeriodType.NONE)
    schedule_type = request.GET.get("schedule_type", ScheduleType.NONE)

    if period_type != PeriodType.NONE:
        templates = templates.filter(period_type=period_type)

    if schedule_type != ScheduleType.NONE:
        templates = templates.filter(schedule_type=schedule_type)

    sorted_templates = templates.annotate(
        is_floating=(
            Q(schedule_type=ScheduleType.FLOATING) & Q(period_type=PeriodType.WEEK)
        )
        | (Q(schedule_type=ScheduleType.FLOATING) & Q(period_type=PeriodType.MONTH))
        | (Q(schedule_type=ScheduleType.FLOATING) & Q(period_type=PeriodType.YEAR)),
        is_fixed=(Q(schedule_type=ScheduleType.FIXED) & Q(period_type=PeriodType.WEEK))
        | (Q(schedule_type=ScheduleType.FIXED) & Q(period_type=PeriodType.MONTH))
        | (Q(schedule_type=ScheduleType.FIXED) & Q(period_type=PeriodType.YEAR)),
    ).order_by(
        "-is_floating",
        "-fixed_weekday",
        "-fixed_day_of_month",
        "-fixed_month_of_year",
        "-next_available_at",
        "-selected_count",
        "-priority",
        "-last_used_at",
    )
    return sorted_templates


def get_block_data(block_id, user):
    block_data = None
    block = None

    if block_id:
        block = get_object_or_404(Block, id=block_id, owner=user)
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
                    "is_hidden": bt.is_hidden,
                }
                for bt in tasks
            ],
        }

    return block, block_data


def update_block_data(block, tasks_list):
    existing_tasks = {t.id: t for t in block.tasks.all()}
    incoming_ids = set()

    for idx, task_data in enumerate(tasks_list):
        task_id = task_data.get("id")
        description = task_data.get("description", "")
        is_encrypted = task_data.get("is_encrypted", False)
        is_hidden = task_data.get("is_hidden", False)

        if is_encrypted:
            password = task_data.get("password")
            decrypted = task_data.get("decrypted")

            if decrypted and password:
                description = encrypt_text(description, password)
            else:
                if task_id and task_id in existing_tasks:
                    description = existing_tasks[task_id].description

        if task_id and task_id in existing_tasks:
            bt = existing_tasks[task_id]
            bt.title = task_data.get("title", bt.title)
            bt.description = description
            bt.amount = task_data.get("amount", bt.amount)
            bt.time = task_data.get("time", bt.time)
            bt.icon = task_data.get("icon", bt.icon)
            bt.is_encrypted = is_encrypted
            bt.is_hidden = is_hidden
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
                is_hidden=is_hidden,
                position=idx,
            )

        incoming_ids.add(bt.id)

    to_delete = set(existing_tasks.keys()) - incoming_ids
    if to_delete:
        BlockTask.objects.filter(id__in=to_delete).delete()
