from django.shortcuts import render
from datetime import datetime

from core.services.weather import fetch_weather, get_day_part, build_periods


def weather_view(request):
    city = request.GET.get("city", "Чебоксары")

    data = fetch_weather(city)

    if "error" in data:
        return render(request, "core/weather.html", {"error": data["error"]})

    hour = datetime.now().hour
    current_part = get_day_part(hour)

    periods = build_periods(current_part)

    return render(
        request,
        "core/weather.html",
        {
            "data": data,
            "periods": periods,
            "current_part": current_part,
        },
    )
