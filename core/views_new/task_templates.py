import os

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from config import settings
from core.forms import TaskTemplateForm
from core.models import TaskTemplate, SystemTaskTemplate
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F

PAGE_SIZE = 50


@login_required
def task_templates_page(request):

    user_task_templates = TaskTemplate.objects.filter(owner=request.user)

    # какие системные шаблоны уже добавлены пользователем
    used_system_ids = user_task_templates.exclude(
        system_template__isnull=True
    ).values_list("system_template_id", flat=True)

    # показываем только те, которых нет
    system_templates = SystemTaskTemplate.objects.exclude(id__in=used_system_ids)

    return render(
        request,
        "core/task_templates/task_templates.html",
        {
            "user_templates": user_task_templates,
            "system_templates": system_templates,
        },
    )


@login_required
def task_template_create(request):
    if request.method == "POST":
        form = TaskTemplateForm(request.POST, request.FILES)

        if form.is_valid():
            template = form.save(commit=False)
            template.owner = request.user
            template.icon = request.FILES.get("icon")

            template.save()

            return redirect("task_templates")

    else:
        form = TaskTemplateForm()

    return render(
        request,
        "core/task_templates/task_template_create.html",
        {"form": form},
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_task_templates(request):
    q = request.GET.get("q", "").strip()
    page = int(request.GET.get("page", 1))

    qs = (
        TaskTemplate.objects.filter(owner=request.user, is_hidden=False)
        .select_related("system_template")
        .order_by("-updated_at")
    )

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    total = qs.count()

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE

    page_items = qs[start:end]
    return Response(
        {
            "results": [serialize_task_template(t, request) for t in page_items],
            "has_next": end < total,
            "page": page,
        }
    )


def serialize_task_template(t: TaskTemplate, request):
    icon = None

    if t.icon and hasattr(t.icon, "url"):
        icon = t.icon.url

    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "icon": request.build_absolute_uri(icon) if icon else None,
        "amount": t.amount,
        "priority": t.priority,
        "period": t.period_type,
        "schedule": t.schedule_type,
        "system_id": t.system_template_id,
        "selected_count": t.selected_count,
        "created_at": t.created_at.strftime("%d.%m.%Y %H:%M"),
        "updated_at": t.updated_at.strftime("%d.%m.%Y %H:%M"),
    }


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_add_system_task_template(request, pk):
    system_template = get_object_or_404(SystemTaskTemplate, pk=pk)

    existing = TaskTemplate.objects.filter(
        owner=request.user, system_template=system_template
    ).first()

    if existing:
        return Response({"error": "exists"}, status=400)

    template = TaskTemplate(
        owner=request.user,
        system_template=system_template,
        title=system_template.title,
        description=system_template.description,
        amount=system_template.amount,
        priority=system_template.priority,
        period_type=system_template.period_type,
        schedule_type=system_template.schedule_type,
        fixed_weekday=system_template.fixed_weekday,
        fixed_day_of_month=system_template.fixed_day_of_month,
        fixed_month_of_year=system_template.fixed_month_of_year,
    )

    # копирование иконки — оставляем как есть
    if system_template.icon:
        icon_path = os.path.join(
            settings.BASE_DIR,
            "static",
            "default_task_templates",
            "icons",
            system_template.icon,
        )
        with open(icon_path, "rb") as f:
            file_name = os.path.basename(system_template.icon)
            template.icon.save(file_name, ContentFile(f.read()), save=False)

    template.save()

    return Response(
        {
            "id": template.id,
            "system_id": system_template.id,
            "title": template.title,
            "description": template.description,
            "icon": template.icon.url if template.icon else None,
            "amount": template.amount,
            "priority": template.priority,
            "period": template.period_type,
            "schedule": template.schedule_type,
            "created_at": template.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": template.updated_at.strftime("%Y-%m-%d %H:%M"),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_add_all_system_task_templates(request):

    system_templates = SystemTaskTemplate.objects.all()

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
            system_template=st,
            title=st.title,
            description=st.description,
            amount=st.amount,
            priority=st.priority,
            period_type=st.period_type,
            schedule_type=st.schedule_type,
            fixed_weekday=st.fixed_weekday,
            fixed_day_of_month=st.fixed_day_of_month,
            fixed_month_of_year=st.fixed_month_of_year,
        )

        if st.icon:
            icon_path = os.path.join(
                settings.BASE_DIR,
                "static",
                "default_task_templates",
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
                "system_id": st.id,
                "title": template.title,
                "description": template.description,
                "icon": template.icon.url if template.icon else None,
                "amount": template.amount,
                "priority": template.priority,
                "period": template.period_type,
                "schedule": template.schedule_type,
            }
        )

    return Response({"added": added})


@login_required
def task_template_create_or_edit(request, template_id=None):
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
            return redirect("task_templates")
    else:
        form = TaskTemplateForm(instance=template)

    return render(
        request,
        "core/task_templates/task_template_create.html",
        {
            "form": form,
            "page_title": page_title,
        },
    )


@login_required
@require_POST
def increment_template_selected(request, template_id):
    TaskTemplate.objects.filter(id=template_id, owner=request.user).update(
        selected_count=F("selected_count") + 1
    )

    return JsonResponse({"status": "ok"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_task_template_delete(request, task_template_id):
    template = get_object_or_404(TaskTemplate, id=task_template_id, owner=request.user)

    system_id = template.system_template.id if template.system_template else None
    affected_blocks = template.block_tasks.count()

    template.delete()

    return Response(
        {
            "status": "ok",
            "system_id": system_id,
            "unlinked_blocks": affected_blocks,
        }
    )
