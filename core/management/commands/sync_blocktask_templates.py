import re
from django.db import transaction
from core.models import (
    BlockTask,
    TaskTemplate,
)  # замените myapp на имя вашего приложения


def normalize_title(title: str) -> str:
    """
    Приводит title к нижнему регистру, убирает лишние пробелы и невидимые символы.
    """
    if not title:
        return ""
    # убираем пробелы в начале/конце, приводим к нижнему регистру
    title = title.strip().lower()
    # заменяем все последовательности пробельных символов на один пробел
    title = re.sub(r"\s+", " ", title)
    return title


@transaction.atomic
def sync_blocktask_templates():
    """
    Сопоставляет BlockTask с TaskTemplate по title без учета регистра,
    учитывает владельца и нормализует пробелы/невидимые символы.
    """
    updated_count = 0

    for bt in BlockTask.objects.select_related("block").all():
        owner = bt.block.owner
        bt_title_norm = normalize_title(bt.title)

        template = TaskTemplate.objects.filter(owner=owner, is_hidden=False).all()

        # ищем первый шаблон, который совпадает по нормализованному title
        matched_template = next(
            (t for t in template if normalize_title(t.title) == bt_title_norm), None
        )

        if matched_template:
            bt.template = matched_template
            bt.save(update_fields=["template"])
            updated_count += 1

    print(f"Обновлено {updated_count} BlockTask с шаблонами.")
