from django.shortcuts import redirect
from django.contrib.auth import logout

from core.forms import RegisterForm

from django.views import View
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from core.models import Device


class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user  # ✔ правильно

        response = super().post(request, *args, **kwargs)

        device_uuid = request.data.get("device_uuid")
        platform = request.data.get("platform")

        if device_uuid and platform == "android":
            Device.objects.update_or_create(
                device_uuid=device_uuid,
                defaults={
                    "user": user,
                    "platform": "android",
                    "last_seen_at": timezone.now(),
                },
            )

        return response


class UserLoginView(View):
    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            # 👉 оставляем (если нужен сайт через cookies)
            login(request, user)

            # 🔥 создаём JWT
            refresh = RefreshToken.for_user(user)

            return JsonResponse(
                {
                    "success": True,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            )

        errors = {}
        for field, msgs in form.errors.items():
            errors[field] = [str(m) for m in msgs]

        return JsonResponse({"success": False, "errors": errors})


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            # 🔥 JWT
            refresh = RefreshToken.for_user(user)

            return JsonResponse(
                {
                    "success": True,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            )

        return JsonResponse({"success": False, "errors": form.errors})


def user_logout(request):
    logout(request)
    return redirect("/")
