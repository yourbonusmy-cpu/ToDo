from django.templatetags.static import static
from django.conf import settings


def get_system_icon_url(icon_name: str, request):
    if not icon_name:
        return ""

    path = f"default_templates/icons/{icon_name}"
    return request.build_absolute_uri(static(path))


def get_media_icon_url(icon_field, request):
    if not icon_field:
        return ""
    return request.build_absolute_uri(icon_field.url)


def resolve_icon(obj, request):
    icon = getattr(obj, "icon", None)

    if not icon:
        return ""

    # ImageField (user icons)
    if hasattr(icon, "url"):
        return request.build_absolute_uri(icon.url)

    # system icon (string)
    if isinstance(icon, str):
        path = f"default_templates/icons/{icon}"
        return request.build_absolute_uri(static(path))

    return ""
