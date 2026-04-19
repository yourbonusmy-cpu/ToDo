from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash
from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

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


# -----------------------------
# 🔢 PIN toggle (AJAX)
# -----------------------------
@login_required
def toggle_pin_view(request):

    if request.method != "POST":
        return JsonResponse({"success": False})

    pin = request.POST.get("pin")

    if not pin or len(pin) != 4 or not pin.isdigit():
        return JsonResponse({"success": False, "error": "PIN должен быть 4 цифры"})

    user_pin, _ = UserPin.objects.get_or_create(user=request.user)

    # 🔴 отключение
    if user_pin.is_pin_enabled:

        if not user_pin.check_pin(pin):
            return JsonResponse({"success": False, "error": "Неверный PIN"})

        user_pin.disable_pin()

        return JsonResponse({"success": True, "action": "disabled"})

    # 🟢 включение
    else:
        user_pin.enable_pin(pin)

        return JsonResponse({"success": True, "action": "enabled"})


@login_required
@require_POST
def verify_pin(request):
    pin = request.POST.get("pin")

    user_pin = getattr(request.user, "userpin", None)
    if not user_pin or not user_pin.is_pin_enabled:
        return JsonResponse({"success": False})

    if not user_pin.check_pin(pin):
        return JsonResponse({"success": False})

    return JsonResponse({"success": True})


@login_required
@require_POST
def set_pin(request):
    pin = request.POST.get("pin")

    if not pin or len(pin) != 4 or not pin.isdigit():
        return JsonResponse({"success": False, "error": "PIN должен быть 4 цифры"})

    user_pin, _ = UserPin.objects.get_or_create(user=request.user)
    user_pin.enable_pin(pin)

    return JsonResponse({"success": True})


@login_required
@require_POST
def disable_pin(request):
    pin = request.POST.get("pin")

    user_pin = getattr(request.user, "userpin", None)
    if not user_pin or not user_pin.is_pin_enabled:
        return JsonResponse({"success": False})

    if not user_pin.check_pin(pin):
        return JsonResponse({"success": False, "error": "Неверный PIN"})

    user_pin.disable_pin()

    return JsonResponse({"success": True})


@login_required
@require_POST
def change_pin_view(request):
    old_pin = request.POST.get("old_pin")
    new_pin = request.POST.get("new_pin")

    user_pin = request.user.userpin

    if not user_pin.check_pin(old_pin):
        return JsonResponse({"success": False, "error": "Неверный PIN"})

    user_pin.enable_pin(new_pin)

    return JsonResponse({"success": True})


# -----------------------------
# 🔐 смена пароля (AJAX)
# -----------------------------
@login_required
def change_password_view(request):

    if request.method != "POST":
        return JsonResponse({"success": False})

    current = request.POST.get("current")
    new = request.POST.get("new")

    if not request.user.check_password(current):
        return JsonResponse({"success": False, "error": "Неверный текущий пароль"})

    if len(new) < 4:
        return JsonResponse({"success": False, "error": "Пароль слишком короткий"})

    request.user.set_password(new)
    request.user.save()
    update_session_auth_hash(request, request.user)

    return JsonResponse({"success": True})


# -----------------------------
# ❌ Удаление аккаунта
# -----------------------------
@login_required
def delete_account_view(request):

    if request.method != "POST":
        return JsonResponse({"success": False})

    password = request.POST.get("password")

    if not request.user.check_password(password):
        return JsonResponse({"success": False, "error": "Неверный пароль"})

    user = request.user
    logout(request)
    user.delete()

    return JsonResponse({"success": True})
