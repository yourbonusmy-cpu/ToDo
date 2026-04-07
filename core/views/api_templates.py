from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from core.models import TaskTemplate

PAGE_SIZE = 50


def serialize_template(t: TaskTemplate):
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "icon": t.icon.url if t.icon else None,
        "amount": t.default_amount,
        "priority": t.priority,
        "period": t.period_type,
        "schedule": t.schedule_type,
        "system_id": t.system_template_id,
        "selected_count": t.selected_count,
        "created_at": t.created_at.strftime("%d.%m.%Y %H:%M"),
        "updated_at": t.updated_at.strftime("%d.%m.%Y %H:%M"),
    }


@login_required
def api_templates(request):

    q = request.GET.get("q", "").strip().lower()
    page = int(request.GET.get("page", 1))

    qs = (
        TaskTemplate.objects.filter(owner=request.user, is_hidden=False)
        .select_related("system_template")
        .order_by("-updated_at")
    )

    # 🔹 фильтрация (Unicode-safe)
    if q:
        filtered = []

        for t in qs:
            title = (t.title or "").lower()
            desc = (t.description or "").lower()

            if q in title or q in desc:
                filtered.append(t)

        qs = filtered
    else:
        qs = list(qs)

    # 🔹 пагинация
    total = len(qs)

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE

    page_items = qs[start:end]

    return JsonResponse(
        {
            "results": [serialize_template(t) for t in page_items],
            "has_next": end < total,
            "page": page,
        }
    )
