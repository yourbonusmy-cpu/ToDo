from datetime import datetime
from django.shortcuts import render

from core.services.weather import (
    get_forecast,
    group_by_period,
    get_day_part,
    build_weather_cards,
    get_wind_direction,
)


def weather_view(request):
    city = request.GET.get("city", "Чебоксары")

    data = get_forecast(city)

    grouped = group_by_period(data["list"], data["city"]["timezone"])

    current_period = get_day_part(datetime.now().hour)

    weather = build_weather_cards(grouped, current_period)

    for w in weather:
        w["wind_dir"] = get_wind_direction(w["wind_deg"])

    cities = [
        "Чебоксары",
        "Москва",
        "Санкт-Петербург",
        "Казань",
        "Новосибирск",
        "Сочи",
        "Анапа",
        "Ялта",
    ]

    return render(
        request,
        "core/weather.html",
        {
            "weather": weather,
            "cities": cities,
            "selected_city": city,
        },
    )
