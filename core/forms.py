from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from core.models import TaskTemplate, GroupTemplate


class TaskTemplateForm(forms.ModelForm):

    class Meta:
        model = TaskTemplate
        fields = [
            "system_template",
            "is_hidden",
            "title",
            "description",
            "icon",  # 👈 ОБЯЗАТЕЛЬНО
            "amount",
            "time",
            "period_type",
            "schedule_type",
            "fixed_weekday",
            "fixed_day_of_month",
            "fixed_month_of_year",
            "priority",
        ]

        widgets = {
            "priority": forms.RadioSelect(
                choices=[
                    (1, "low"),
                    (2, "mid"),
                    (3, "high"),
                ]
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название задачи",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Описание (необязательно)",
                }
            ),
            "fixed_day_of_month": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 31,
                    "class": "form-control",
                }
            ),
            "time": forms.NumberInput(
                attrs={
                    "min": 0,  # 👈 минимум 0
                    "max": 24,  # 👈 максимум 24
                    "step": 1,  # 👈 шаг (1 час)
                    "class": "form-control text-center",
                    "placeholder": "часы",
                }
            ),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Логин"})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Пароль"}
        )
    )


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class GroupTemplateForm(forms.ModelForm):
    class Meta:
        model = GroupTemplate
        fields = ["title", "description", "tasks"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "tasks": forms.SelectMultiple(attrs={"class": "form-select", "size": 10}),
        }
