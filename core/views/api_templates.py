from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from core.models import TaskTemplate
from core.utils.icons import resolve_icon

PAGE_SIZE = 50


def serialize_template(t: TaskTemplate, request):
    icon = None

    if t.icon and hasattr(t.icon, "url"):
        icon = t.icon.url

    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "icon": request.build_absolute_uri(icon) if icon else None,
        "amount": t.default_amount,
        "priority": t.priority,
        "period": t.period_type,
        "schedule": t.schedule_type,
        "system_id": t.system_template_id,
        "selected_count": t.selected_count,
        "created_at": t.created_at.strftime("%d.%m.%Y %H:%M"),
        "updated_at": t.updated_at.strftime("%d.%m.%Y %H:%M"),
    }


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

PAGE_SIZE = 50


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_templates(request):

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
            "results": [serialize_template(t, request) for t in page_items],
            "has_next": end < total,
            "page": page,
        }
    )
