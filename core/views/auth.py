from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from core.forms import RegisterForm


class UserLoginView(LoginView):
    template_name = "auth/login.html"


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")

    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("/")
