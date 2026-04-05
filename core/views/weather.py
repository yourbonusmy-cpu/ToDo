from datetime import datetime
from django.shortcuts import render

from core.services.weather import (
    # get_forecast,
    group_by_period,
    get_day_part,
    build_weather_cards,
    get_wind_direction,
    normalize_weather,
    get_weather_ui,
)

from core.services.weather_open_meteo import get_forecast


def weather_view(request):
    city = request.GET.get("city", "Чебоксары")

    data = get_forecast(city)

    grouped = group_by_period(data["list"])

    current_hour = datetime.now().hour
    current_period = get_day_part(current_hour)

    weather = build_weather_cards(grouped, current_period)

    for w in weather:
        w["wind_dir"] = get_wind_direction(w["wind_deg"])

        w["description"] = normalize_weather(w["main"], w["clouds"])

        icon, color = get_weather_ui(w["main"], w["clouds"])

        w["icon"] = icon
        w["color"] = color

    cities = [
        "Чебоксары",
        "Москва",
        "Санкт-Петербург",
        "Казань",
        "Новосибирск",
        "Архангельск",
        "Мурманск",
        "Магадан",
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
