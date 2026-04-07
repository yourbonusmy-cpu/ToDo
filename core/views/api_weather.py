from django.http import JsonResponse
from datetime import datetime

from core.services.weather import (
    get_forecast,
    group_by_period,
    get_day_part,
    build_weather_cards,
    get_wind_direction,
)


def weather_api(request):
    city = request.GET.get("city", "Чебоксары")

    data = get_forecast(city)

    grouped = group_by_period(data["list"], data["city"]["timezone"])
    current_period = get_day_part(datetime.now().hour)

    weather = build_weather_cards(grouped, current_period)

    for w in weather:
        w["wind_dir"] = get_wind_direction(w["wind_deg"])

    return JsonResponse({"weather": weather})
