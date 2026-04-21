from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.views import View

from core.forms import RegisterForm

from django.http import JsonResponse
from django.contrib.auth import login


from django.views import View
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from rest_framework_simplejwt.tokens import RefreshToken


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


from rest_framework_simplejwt.tokens import RefreshToken


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
