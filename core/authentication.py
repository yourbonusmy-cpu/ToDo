# app/authentication.py

from rest_framework.authentication import BaseAuthentication
from django.utils import timezone
from .models import Device


class DeviceAuthentication(BaseAuthentication):

    def authenticate(self, request):
        device_id = request.headers.get("X-Device-Id")
        platform = request.headers.get("X-Platform")

        # игнорируем браузер и прочих клиентов
        if not device_id or platform != "android":
            return None

        # важно: пользователь должен уже быть установлен предыдущим классом (JWT)
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None

        # upsert устройства
        device, _ = Device.objects.update_or_create(
            device_id=device_id,
            defaults={
                "user": user,
                "platform": "android",
                "is_active": True,
                "last_seen_at": timezone.now(),
            },
        )

        # можно сохранить на request для дальнейшего использования
        request.device = device

        # не подменяем пользователя
        return None
