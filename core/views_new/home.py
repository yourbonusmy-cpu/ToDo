from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Prefetch
from core.models import Block, BlockTask
from django.shortcuts import render
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.styles import Font, Alignment
import os
import json
import zipfile
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse


from django.db.models import Prefetch
from core.models import Block, BlockTask, TaskTemplate  # 👈 добавить


def home(request):
    if not request.user.is_authenticated:
        return render(request, "core/landing.html")

    blocks_qs = (
        Block.objects.filter(owner=request.user, is_hidden=False)
        .prefetch_related(
            Prefetch(
                "block_tasks",
                queryset=BlockTask.objects.order_by("position"),
            )
        )
        .order_by("-created_at")
    )

    paginator = Paginator(blocks_qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ✅ Только пользовательские шаблоны
    system_tasks = TaskTemplate.objects.filter(owner=request.user).order_by("title")

    return render(
        request,
        "core/blocks/dashboard.html",
        {
            "page_obj": page_obj,
            "blocks": page_obj.object_list,
            "system_tasks": system_tasks,
        },
    )
