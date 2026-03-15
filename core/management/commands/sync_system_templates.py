# python manage.py sync_system_templates
import json
import os
from django.core.management.base import BaseCommand
from core.models import SystemTaskTemplate
from django.conf import settings


class Command(BaseCommand):
    help = "Синхронизирует системные шаблоны задач из static/templates.json"

    def handle(self, *args, **kwargs):
        # Путь к файлу templates.json
        templates_path = os.path.join(
            settings.BASE_DIR, "static", "default_templates", "templates.json"
        )

        if not os.path.exists(templates_path):
            self.stdout.write(self.style.ERROR(f"{templates_path} не найден!"))
            return

        # Загружаем JSON
        with open(templates_path, "r", encoding="utf-8") as f:
            try:
                json_templates = json.load(f)
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f"Ошибка чтения JSON: {e}"))
                return

        for template in json_templates:
            obj, created = SystemTaskTemplate.objects.update_or_create(
                code=template["code"],
                defaults={
                    "title": template.get("title", ""),
                    "description": template.get("description", ""),
                    "icon": template.get("icon", ""),
                    "default_amount": template.get("default_amount", 1),
                    "period_type": template.get("period_type", "day"),
                    "schedule_type": template.get("schedule_type", "fixed"),
                    "priority": template.get("priority", 1),
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан шаблон: {obj.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Обновлен шаблон: {obj.title}"))

        self.stdout.write(
            self.style.SUCCESS("Синхронизация системных шаблонов завершена.")
        )
