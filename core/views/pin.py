from datetime import timedelta

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST
from core.models import UserPin


def lock_pin(request):
    user_pin = getattr(request.user, "userpin", None)

    if not user_pin or not user_pin.is_pin_enabled:
        return JsonResponse({"success": False})

    request.session["pin_locked"] = True
    return JsonResponse({"success": True})


@login_required
@require_POST
def unlock_pin__(request):

    pin = request.POST.get("pin")

    if not pin or len(pin) != 4 or not pin.isdigit():
        return JsonResponse({"success": False})

    try:
        user_pin = UserPin.objects.get(user=request.user)
    except UserPin.DoesNotExist:
        return JsonResponse({"success": False})

    if user_pin.check_pin(pin):
        request.session["pin_locked"] = False
        return JsonResponse({"success": True})

    return JsonResponse({"success": False})


@login_required
def pin_unlock_page(request):
    return render(request, "core/pin_unlock.html")


@login_required
@require_POST
def unlock_pin(request):
    pin = request.POST.get("pin")
    if not pin or len(pin) != 4 or not pin.isdigit():
        return JsonResponse({"success": False})

    user_pin = getattr(request.user, "userpin", None)
    if not user_pin or not user_pin.is_pin_enabled:
        return JsonResponse({"success": False})

    # Проверка cooldown
    cooldown_until = request.session.get("pin_cooldown_until")
    now = timezone.now().timestamp()
    if cooldown_until and now < cooldown_until:
        remaining = int(cooldown_until - now)
        return JsonResponse({"success": False, "cooldown": remaining})

    # Инициализация счётчика ошибок
    errors = request.session.get("pin_errors", 0)

    if user_pin.check_pin(pin):
        # Сброс ошибок и cooldown
        request.session["pin_errors"] = 0
        request.session["pin_cooldown_until"] = None
        request.session["pin_locked"] = False
        return JsonResponse({"success": True})

    # Неверный PIN
    errors += 1
    request.session["pin_errors"] = errors

    if errors >= 3:
        # Включаем cooldown 30 секунд
        cooldown_seconds = 30
        request.session["pin_cooldown_until"] = (
            timezone.now() + timedelta(seconds=cooldown_seconds)
        ).timestamp()
        request.session["pin_errors"] = 0  # сбросим счётчик
        return JsonResponse({"success": False, "cooldown": cooldown_seconds})

    return JsonResponse({"success": False, "errors": errors})
