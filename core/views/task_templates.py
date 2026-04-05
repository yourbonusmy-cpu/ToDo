# core/views/task_templates.py
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import F
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from ..models import TaskTemplate, SystemTaskTemplate
from ..forms import TaskTemplateForm


@login_required
@require_POST
def increment_template_selected(request, template_id):
    print(f"template_id: {template_id}")
    TaskTemplate.objects.filter(id=template_id, owner=request.user).update(
        selected_count=F("selected_count") + 1
    )

    return JsonResponse({"status": "ok"})


@login_required
def task_template_create_view(request):
    templates = TaskTemplate.objects.filter(owner=request.user).order_by("-created_at")

    if request.method == "POST":
        form = TaskTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            return redirect("task_template_create")  # редирект на ту же страницу
    else:
        form = TaskTemplateForm()

    return render(
        request,
        "core/task_template_create.html",
        {"form": form, "templates": templates},
    )


@login_required
def templates_list(request):
    user_templates = TaskTemplate.objects.filter(owner=request.user)
    return render(request, "core/templates.html", {"user_templates": user_templates})


@login_required
def template_create_or_edit(request, template_id=None):
    if template_id:
        template = get_object_or_404(TaskTemplate, id=template_id, owner=request.user)
        page_title = "Редактирование шаблона задачи"
    else:
        template = None
        page_title = "Создание шаблона задачи"

    if request.method == "POST":
        form = TaskTemplateForm(request.POST, request.FILES, instance=template)
        if form.is_valid():
            new_template = form.save(commit=False)
            new_template.owner = request.user
            new_template.save()
            return redirect("templates")
    else:
        form = TaskTemplateForm(instance=template)

    return render(
        request,
        "core/task_template_create.html",
        {
            "form": form,
            "page_title": page_title,
        },
    )


@login_required
def template_delete(request, template_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    template = get_object_or_404(TaskTemplate, id=template_id, owner=request.user)
    system_id = template.system_template.id if template.system_template else None

    # Считаем блоки, которые будут "отвязаны"
    affected_blocks = template.block_tasks.count()

    template.delete()  # при SET_NULL ссылки обнуляются автоматически

    return JsonResponse(
        {"status": "ok", "system_id": system_id, "unlinked_blocks": affected_blocks}
    )


@login_required
def template_create(request):

    if request.method == "POST":
        form = TaskTemplateForm(request.POST, request.FILES)

        if form.is_valid():
            template = form.save(commit=False)
            template.owner = request.user
            template.save()

            return redirect("templates")

    else:
        form = TaskTemplateForm()

    return render(
        request,
        "core/task_template_create.html",
        {"form": form},
    )


@login_required
def add_system_template_ajax(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    system_template = get_object_or_404(SystemTaskTemplate, pk=pk)

    # Проверяем, не добавлял ли пользователь уже этот системный шаблон
    existing = TaskTemplate.objects.filter(
        owner=request.user, system_template=system_template
    ).first()

    if existing:
        return JsonResponse(
            {"error": "Template already exists", "id": existing.id}, status=400
        )

    template = TaskTemplate(
        owner=request.user,
        system_template=system_template,  # ← ВАЖНО
        title=system_template.title,
        description=system_template.description,
        default_amount=system_template.default_amount,
        priority=system_template.priority,
        period_type=system_template.period_type,
        schedule_type=system_template.schedule_type,
        fixed_weekday=system_template.fixed_weekday,
        fixed_day_of_month=system_template.fixed_day_of_month,
        fixed_month_of_year=system_template.fixed_month_of_year,
    )

    # копируем иконку
    if system_template.icon:
        icon_path = os.path.join(
            settings.BASE_DIR,
            "static",
            "default_templates",
            "icons",
            system_template.icon,
        )

        with open(icon_path, "rb") as f:
            file_name = os.path.basename(system_template.icon)
            template.icon.save(file_name, ContentFile(f.read()), save=False)

    template.save()

    return JsonResponse(
        {
            "id": template.id,
            "system_id": system_template.id,  # <-- передаем system_id
            "title": template.title,
            "description": template.description,
            "icon": template.icon.url if template.icon else None,
            "amount": template.default_amount,
            "priority": template.priority,
            "period": template.period_type,
            "schedule": template.schedule_type,
            "created_at": template.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": template.updated_at.strftime("%Y-%m-%d %H:%M"),
        }
    )


@login_required
def add_all_system_templates(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    system_templates = SystemTaskTemplate.objects.all()

    # какие системные шаблоны уже добавлены
    existing_system_ids = set(
        TaskTemplate.objects.filter(
            owner=request.user, system_template__isnull=False
        ).values_list("system_template_id", flat=True)
    )

    added = []

    for st in system_templates:

        if st.id in existing_system_ids:
            continue

        template = TaskTemplate(
            owner=request.user,
            system_template=st,  # ← ВАЖНО
            title=st.title,
            description=st.description,
            default_amount=st.default_amount,
            priority=st.priority,
            period_type=st.period_type,
            schedule_type=st.schedule_type,
            fixed_weekday=st.fixed_weekday,
            fixed_day_of_month=st.fixed_day_of_month,
            fixed_month_of_year=st.fixed_month_of_year,
        )

        # копируем иконку
        if st.icon:
            icon_path = os.path.join(
                settings.BASE_DIR,
                "static",
                "default_templates",
                "icons",
                st.icon,
            )

            with open(icon_path, "rb") as f:
                file_name = os.path.basename(st.icon)
                template.icon.save(file_name, ContentFile(f.read()), save=False)

        template.save()

        added.append(
            {
                "id": template.id,
                "system_id": st.id,  # <-- передаем system_id
                "title": template.title,
                "description": template.description,
                "icon": template.icon.url if template.icon else None,
                "amount": template.default_amount,
                "priority": template.priority,
                "period": template.period_type,
                "schedule": template.schedule_type,
            }
        )

    return JsonResponse({"added": added})


@login_required
def templates_page(request):

    user_templates = TaskTemplate.objects.filter(owner=request.user)

    # какие системные шаблоны уже добавлены пользователем
    used_system_ids = user_templates.exclude(system_template__isnull=True).values_list(
        "system_template_id", flat=True
    )

    # показываем только те, которых нет
    system_templates = SystemTaskTemplate.objects.exclude(id__in=used_system_ids)

    return render(
        request,
        "core/templates.html",
        {
            "user_templates": user_templates,
            "system_templates": system_templates,
        },
    )
