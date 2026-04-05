from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.views import View

from core.forms import RegisterForm

from django.http import JsonResponse
from django.contrib.auth import login


class UserLoginView(View):
    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({"success": True})

        # Сбор ошибок из формы
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

            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "errors": form.errors})


def user_logout(request):
    logout(request)
    return redirect("/")
