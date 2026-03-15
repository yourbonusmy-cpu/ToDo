from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Prefetch

from core.models import Block, BlockTask


def home(request):
    if not request.user.is_authenticated:
        return render(request, "core/landing.html")

    blocks_qs = (
        Block.objects.filter(owner=request.user)
        .prefetch_related(
            Prefetch(
                "tasks",  # related_name из BlockTask
                queryset=BlockTask.objects.order_by("position"),  # без select_related
            )
        )
        .order_by("-created_at")
    )

    paginator = Paginator(blocks_qs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/dashboard.html",
        {
            "page_obj": page_obj,
            "blocks": page_obj.object_list,
        },
    )


@login_required
def block_detail(request, block_id):
    block = get_object_or_404(Block, id=block_id, owner=request.user)
    block_tasks = block.tasks.order_by("position")
    return render(
        request,
        "core/block_detail.html",
        {"m_block": block, "block_tasks": block_tasks},
    )
