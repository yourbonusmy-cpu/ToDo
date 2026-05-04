from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth import get_user_model

from core.models import TaskTemplate, Block, GroupTemplate, UserPin, BlockTask

User = get_user_model()


@login_required
def profile_view(request):

    user = request.user

    templates_count = TaskTemplate.objects.filter(owner=user).count()
    blocks_count = Block.objects.filter(owner=user).count()
    groups_count = GroupTemplate.objects.filter(owner=user).count()

    top_templates = (
        BlockTask.objects.filter(
            block__owner=request.user, template__isnull=False, is_hidden=False
        )
        .values("template", "template__title", "template__icon")  # 👈 группировка
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    user_pin, _ = UserPin.objects.get_or_create(user=user)

    return render(
        request,
        "core/profile.html",
        {
            "templates_count": templates_count,
            "blocks_count": blocks_count,
            "groups_count": groups_count,
            "top_templates": top_templates,
            "user_pin": user_pin,
        },
    )
