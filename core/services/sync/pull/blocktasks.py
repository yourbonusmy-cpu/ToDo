from django.conf import settings

from core.models import BlockTask


def get_blocktasks(request, last_sync):
    qs = BlockTask.objects.filter(block__owner=request.user)

    if last_sync:
        qs = qs.filter(updated_at__gt=last_sync)

    # Получаем данные
    data = list(
        qs.values(
            "uuid",
            "block__uuid",
            "template__uuid",
            "title",
            "description",
            "amount",
            "time",
            "position",
            "is_hidden",
            "is_encrypted",
            "icon",
            "updated_at",
        )
    )

    # Добавляем полный URL к иконке
    for item in data:
        icon_path = item.get("icon")

        if icon_path and icon_path.strip():  # если иконка есть и не пустая строка
            # Убираем ведущий слеш, если он есть, чтобы не было двойного //
            icon_path = icon_path.lstrip("/")

            # Формируем полный URL
            item["icon"] = request.build_absolute_uri(settings.MEDIA_URL + icon_path)
        else:
            item["icon"] = None  # лучше возвращать None, чем пустую строку

    return data
