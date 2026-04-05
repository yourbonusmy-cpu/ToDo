import requests
from datetime import datetime
from collections import defaultdict
from django.conf import settings


# ---------- API ----------
def get_forecast(city: str):
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
    }

    return requests.get(url, params=params).json()


# ---------- период ----------
def get_day_part(hour: int) -> str:
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "day"
    elif 18 <= hour < 24:
        return "evening"
    else:
        return "night"


def detect_period(hour: int):
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "day"
    elif 18 <= hour < 24:
        return "evening"
    return "night"


# ---------- группировка ----------
def group_by_period(forecast_list):
    grouped = defaultdict(list)

    for item in forecast_list:
        dt = datetime.fromtimestamp(item["dt"])
        period = detect_period(dt.hour)
        grouped[period].append(item)

    return grouped


# ---------- агрегация ----------
def aggregate_period(data_list):
    closest = get_closest_weather(data_list)

    temps = [d["main"]["temp"] for d in data_list]
    humidities = [d["main"]["humidity"] for d in data_list]
    pressures = [d["main"]["pressure"] for d in data_list]
    winds = [d["wind"]["speed"] for d in data_list]

    return {
        "temp": round(sum(temps) / len(temps), 1),
        "humidity": round(sum(humidities) / len(humidities)),
        "pressure": round(sum(pressures) / len(pressures)),
        "wind_speed": round(sum(winds) / len(winds), 1),
        # 🔑 ключевые поля берём из closest
        "wind_deg": closest["wind"].get("deg", 0),
        "main": closest["weather"][0]["main"],
        "description": closest["weather"][0]["description"],
        "clouds": closest.get("clouds", {}).get("all", 0),
    }


# ---------- ветер ----------
def get_wind_direction(deg: int) -> str:
    directions = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    return directions[round(deg / 45) % 8]


# ---------- нормализация ----------
def normalize_weather(main: str, clouds: int) -> str:
    if main == "Clear":
        return "Ясно"

    if main == "Clouds":
        if clouds < 20:
            return "Малооблачно"
        elif clouds < 50:
            return "Переменная облачность"
        elif clouds < 80:
            return "Облачно"
        else:
            return "Пасмурно"

    mapping = {
        "Rain": "Дождь",
        "Snow": "Снег",
        "Thunderstorm": "Гроза",
        "Drizzle": "Морось",
        "Mist": "Туман",
        "Fog": "Туман",
        "Haze": "Дымка",
    }

    return mapping.get(main, main)


def get_weather_ui(main: str, clouds: int):
    if main == "Clear":
        return "☀️", "weather-clear"

    if main == "Clouds":
        if clouds < 20:
            return "🌤", "weather-clear"
        elif clouds < 50:
            return "⛅", "weather-clouds"
        elif clouds < 80:
            return "☁️", "weather-clouds"
        else:
            return "🌥", "weather-clouds"

    mapping = {
        "Rain": ("🌧", "weather-rain"),
        "Snow": ("❄️", "weather-snow"),
        "Thunderstorm": ("⛈", "weather-thunder"),
    }

    return mapping.get(main, ("🌡", "weather-default"))


# ---------- логика 4 карточек ----------
def build_period_sequence(current):
    if current == "morning":
        return ["morning", "day", "evening", "night"]

    elif current == "day":
        return ["day", "evening", "night", "next_morning"]

    elif current == "evening":
        return ["evening", "night", "next_morning", "next_evening"]

    else:  # night
        return ["night", "next_morning", "day", "evening"]


def build_fixed_day_weather(grouped):
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

        data = aggregate_period(grouped[key])

        result.append({"label": ru_map[key], **data})

    return result


def get_current_weather(forecast_list):
    now = datetime.now()

    closest = min(
        forecast_list, key=lambda d: abs(datetime.fromtimestamp(d["dt"]) - now)
    )

    return {
        "temp": closest["main"]["temp"],
        "humidity": closest["main"]["humidity"],
        "pressure": closest["main"]["pressure"],
        "wind_speed": closest["wind"]["speed"],
        "wind_deg": closest["wind"].get("deg", 0),
        "clouds": closest.get("clouds", {}).get("all", 50),
        "main": closest["weather"][0]["main"],
        "description": closest["weather"][0]["description"],
    }


def get_closest_weather(data_list):
    now = datetime.now()

    closest = min(data_list, key=lambda d: abs(datetime.fromtimestamp(d["dt"]) - now))

    return closest


def build_weather_cards(grouped, current_period):
    ru_map = {
        "morning": "Утро",
        "day": "День",
        "evening": "Вечер",
        "night": "Ночь",
        "next_morning": "Завтра утро",
        "next_evening": "Завтра вечер",
    }

    sequence = build_period_sequence(current_period)

    result = []

    for i, key in enumerate(sequence):
        base_key = key.replace("next_", "")

        if base_key not in grouped:
            continue

        data = aggregate_period(grouped[base_key])

        result.append({"label": ru_map[key], "is_current": i == 0, **data})

    return result
