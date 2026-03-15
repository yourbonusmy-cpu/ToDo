# core/templatetags/block_tags.py
from django import template
import json

register = template.Library()


@register.filter
def block_json_script(block, element_id):
    """
    Возвращает JSON блока с задачами для редактирования.
    """
    tasks = []
    for bt in block.blocktask_set.all():
        t = bt.task
        tasks.append(
            {
                "template_id": t.template.id,
                "id": t.id,
                "title": t.template.title,
                "description": t.description,
                "amount": t.amount,
                "time": t.time,
                "icon": t.template.icon.url if t.template.icon else "",
            }
        )
    data = {"id": block.id, "title": block.title, "tasks": tasks}
    return (
        f'<script type="application/json" id="{element_id}">{json.dumps(data)}</script>'
    )
