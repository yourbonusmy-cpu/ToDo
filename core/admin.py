from django.contrib import admin

from core.models import TaskTemplate


# Register your models here.
@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "period_type",
        "schedule_type",
        "priority",
        "created_at",
    )