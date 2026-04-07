import requests
from datetime import datetime, timedelta
from collections import defaultdict
from django.conf import settings

# ================= API =================


def get_forecast(city: str):
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
    }

    return requests.get(url, params=params).json()


# ================= ПЕРИОД =================


def detect_period(hour: int):
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "day"
    elif 18 <= hour < 24:
        return "evening"
    return "night"


def get_day_part(hour: int):
    return detect_period(hour)


# ================= ГРУППИРОВКА =================


def group_by_period(forecast_list, tz_offset):
    grouped = defaultdict(list)

    for item in forecast_list:
        dt = datetime.utcfromtimestamp(item["dt"]) + timedelta(seconds=tz_offset)
        period = detect_period(dt.hour)
        grouped[period].append(item)

    return grouped


# ================= ВЫБОР ТОЧНОГО СЛОТА =================


def pick_representative(data_list):
    """
    Выбираем наиболее релевантный слот:
    - приоритет: ближайший ко времени периода
    - fallback: просто ближайший к текущему времени
    """
    now = datetime.now()

    return min(data_list, key=lambda d: abs(datetime.fromtimestamp(d["dt"]) - now))


# ================= НОРМАЛИЗАЦИЯ =================


def normalize_weather(item):
    main = item["weather"][0]["main"]
    desc = item["weather"][0]["description"]
    clouds = item.get("clouds", {}).get("all", 0)
    pop = item.get("pop", 0)
    icon_code = item["weather"][0]["icon"]

    is_night = icon_code.endswith("n")

    # осадки
    if pop > 0.6:
        return "Дождь"
    elif pop > 0.3:
        return "Небольшой дождь"

    # ясно
    if main == "Clear":
        return "Ясно" if is_night else "Солнечно"

    # облака
    if main == "Clouds":
        if clouds < 10:
            return "Ясно" if is_night else "Солнечно"
        elif clouds < 25:
            return "Малооблачно"
        elif clouds < 60:
            return "Переменная облачность"
        elif clouds < 85:
            return "Облачно"
        else:
            return "Пасмурно"

    mapping = {
        "Rain": "Дождь",
        "Drizzle": "Морось",
        "Thunderstorm": "Гроза",
        "Snow": "Снег",
        "Mist": "Туман",
        "Fog": "Туман",
        "Haze": "Дымка",
    }

    return mapping.get(main, desc)


# ================= UI =================


def get_weather_ui(item):
    main = item["weather"][0]["main"]
    clouds = item.get("clouds", {}).get("all", 0)
    pop = item.get("pop", 0)
    icon_code = item["weather"][0]["icon"]

    is_night = icon_code.endswith("n")

    # осадки
    if pop > 0.5:
        return "🌧", "weather-rain"

    # ясно
    if main == "Clear":
        return ("🌙", "weather-clear") if is_night else ("☀️", "weather-clear")

    # облака
    if main == "Clouds":
        if clouds < 25:
            return ("🌙", "weather-clear") if is_night else ("🌤", "weather-clear")
        elif clouds < 60:
            return ("☁️", "weather-clouds")
        else:
            return ("🌥", "weather-clouds")

    return "🌡", "weather-default"


# ================= КАРТОЧКИ =================


def build_weather_cards(grouped, current_period):
    order = ["morning", "day", "evening", "night"]

    ru_map = {
        "morning": "Утро",
        "day": "День",
        "evening": "Вечер",
        "night": "Ночь",
    }

    result = []

    for key in order:
        if key not in grouped:
            continue

        item = pick_representative(grouped[key])

        result.append(
            {
                "label": ru_map[key],
                "is_current": key == current_period,
                "temp": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "wind_speed": item["wind"]["speed"],
                "wind_deg": item["wind"].get("deg", 0),
                "clouds": item.get("clouds", {}).get("all", 0),
                "description": normalize_weather(item),
                "icon_code": item["weather"][0]["icon"],
                "icon": get_weather_ui(item)[0],
                "color": get_weather_ui(item)[1],
            }
        )

    return result


# ================= ВЕТЕР =================


def get_wind_direction(deg: int) -> str:
    directions = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    return directions[round(deg / 45) % 8]
