import requests
from datetime import datetime
from collections import defaultdict

# координаты городов (важно!)
CITY_COORDS = {
    "Москва": (55.75, 37.61),
    "Чебоксары": (56.13, 47.25),
    "Санкт-Петербург": (59.93, 30.31),
    "Казань": (55.79, 49.12),
    "Новосибирск": (55.03, 82.92),
}


# ---------- API ----------
def get_forecast(city: str):
    lat, lon = CITY_COORDS.get(city, CITY_COORDS["Москва"])

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "temperature_2m",
            "relativehumidity_2m",
            "pressure_msl",
            "windspeed_10m",
            "winddirection_10m",
            "weathercode",
        ],
        "timezone": "auto",
    }

    data = requests.get(url, params=params).json()

    return transform_to_common_format(data)


# ---------- преобразование ----------
def transform_to_common_format(data):
    result = []

    hourly = data["hourly"]

    for i in range(len(hourly["time"])):
        dt = datetime.fromisoformat(hourly["time"][i])

        result.append(
            {
                "dt": int(dt.timestamp()),
                "main": {
                    "temp": hourly["temperature_2m"][i],
                    "humidity": hourly["relativehumidity_2m"][i],
                    "pressure": hourly["pressure_msl"][i],
                },
                "wind": {
                    "speed": hourly["windspeed_10m"][i],
                    "deg": hourly["winddirection_10m"][i],
                },
                "weather": [
                    {
                        "main": weather_code_to_main(hourly["weathercode"][i]),
                        "description": weather_code_to_desc(hourly["weathercode"][i]),
                    }
                ],
            }
        )

    return {"list": result}


def weather_code_to_main(code: int):
    if code == 0:
        return "Clear"
    elif code in [1, 2, 3]:
        return "Clouds"
    elif code in [45, 48]:
        return "Mist"
    elif code in [51, 53, 55]:
        return "Drizzle"
    elif code in [61, 63, 65]:
        return "Rain"
    elif code in [71, 73, 75]:
        return "Snow"
    elif code in [95, 96, 99]:
        return "Thunderstorm"
    return "Clouds"


def weather_code_to_desc(code: int):
    mapping = {
        0: "Ясно",
        1: "Преимущественно ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Туман",
        51: "Морось",
        53: "Морось",
        55: "Морось",
        61: "Дождь",
        63: "Дождь",
        65: "Сильный дождь",
        71: "Снег",
        73: "Снег",
        75: "Сильный снег",
        95: "Гроза",
    }
    return mapping.get(code, "Облачно")
