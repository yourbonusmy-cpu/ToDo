import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import GroupTemplate, TaskTemplate


@login_required
def group_templates_list(request):

    groups = (
        GroupTemplate.objects.filter(owner=request.user)
        .prefetch_related("tasks")
        .order_by("-updated_at")
    )

    return render(
        request,
        "core/group_templates.html",
        {"groups": groups},
    )


@login_required
def group_template_create_or_edit(request, group_id=None):

    group = None

    if group_id:
        group = get_object_or_404(GroupTemplate, id=group_id, owner=request.user)

    templates = TaskTemplate.objects.filter(owner=request.user)

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        tasks = json.loads(request.POST.get("tasks", "[]"))

        if group is None:

            group = GroupTemplate.objects.create(
                owner=request.user,
                title=title,
                description=description,
            )

        else:

            group.title = title
            group.description = description
            group.save()

        selected_templates = TaskTemplate.objects.filter(
            id__in=tasks, owner=request.user
        )

        group.tasks.set(selected_templates)

        return redirect("group_templates")

    group_json = None

    if group:

        group_json = json.dumps(
            {
                "id": group.id,
                "title": group.title,
                "description": group.description,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "icon": t.icon.url if t.icon else "",
                    }
                    for t in group.tasks.all()
                ],
            }
        )

    return render(
        request,
        "core/group_template_create.html",
        {
            "templates": templates,
            "group_json": group_json,
            "group": group,
        },
    )


@login_required
def group_template_delete(request, group_id):

    group = get_object_or_404(
        GroupTemplate,
        id=group_id,
        owner=request.user,
    )

    group.delete()

    return JsonResponse({"success": True})


@login_required
def api_group_detail(request, group_id):

    group = get_object_or_404(
        GroupTemplate.objects.prefetch_related("tasks"),
        id=group_id,
        owner=request.user,
    )

    tasks = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "amount": t.default_amount,
            "icon": t.icon.url if t.icon else "",
        }
        for t in group.tasks.all()
    ]

    return JsonResponse({"tasks": tasks})
