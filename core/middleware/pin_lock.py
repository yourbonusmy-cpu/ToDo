# middleware.py

from django.shortcuts import redirect
from django.urls import reverse


class PinLockMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Если пользователь не авторизован — ничего не делаем
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Если PIN не активирован — пропускаем
        if not request.session.get("pin_locked"):
            return self.get_response(request)

        # Разрешённые URL
        allowed_urls = [
            reverse("pin_unlock"),
            reverse("lock_pin"),
            reverse("unlock_pin"),
            reverse("login"),
            reverse("logout"),
        ]

        # Если текущий путь разрешён — пропускаем
        if request.path in allowed_urls:
            return self.get_response(request)

        # Иначе блокируем
        return redirect("pin_unlock")
