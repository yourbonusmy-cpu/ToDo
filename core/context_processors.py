# core/context_processors.py

from core.models import UserPin

def pin_context(request):

    if not request.user.is_authenticated:
        return {"PIN_ENABLED": False}

    user_pin = getattr(request.user, "userpin", None)

    return {
        "PIN_ENABLED": user_pin.is_pin_enabled if user_pin else False
    }