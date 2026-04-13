from django import template
import math

register = template.Library()


@register.filter
def clock_icon_index(value):
    """
    Преобразует время в диапазон 1–12 (как часы)
    """
    try:
        t = int(float(value))  # на случай 9.0
    except:
        return 1

    result = t % 12
    return result if result != 0 else 12
