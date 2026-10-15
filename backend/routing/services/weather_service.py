import time
from datetime import UTC, datetime

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

HOURLY_VARIABLES = [
    "temperature_2m",
    "precipitation",
    "snowfall",
    "wind_speed_10m",
    "wind_gusts_10m",
    "weather_code",
]

RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

MAX_RETRIES = 2
REQUEST_TIMEOUT = 20
RETRY_DELAY = 2


def request_weather_forecast(params):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                OPEN_METEO_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code in RETRY_STATUS_CODES:
                print(
                    f"Weather API temporarily unavailable. "
                    f"Status: {response.status_code}. "
                    f"Attempt: {attempt + 1}/{MAX_RETRIES}"
                )

                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue

                return None

            response.raise_for_status()

            return response.json()

        except requests.Timeout:
            print(
                f"Weather API request timed out. Attempt: {attempt + 1}/{MAX_RETRIES}"
            )

            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue

            return None

        except requests.ConnectionError:
            print(
                f"Weather API connection failed. Attempt: {attempt + 1}/{MAX_RETRIES}"
            )

            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue

            return None

        except requests.RequestException:
            print("Weather API request failed.")
            return None

        except ValueError:
            print("Weather API returned invalid JSON.")
            return None

    return None


def fetch_checkpoint_weather(checkpoints):
    if not checkpoints:
        return checkpoints

    latitudes = ",".join(str(checkpoint["latitude"]) for checkpoint in checkpoints)

    longitudes = ",".join(str(checkpoint["longitude"]) for checkpoint in checkpoints)

    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "hourly": ",".join(HOURLY_VARIABLES),
        "timezone": "UTC",
        "forecast_days": 16,
        "wind_speed_unit": "mph",
        "temperature_unit": "fahrenheit",
    }

    weather_results = request_weather_forecast(params)

    if weather_results is None:
        print(
            "Weather forecast unavailable. Returning checkpoints without weather data."
        )

        for checkpoint in checkpoints:
            checkpoint["weather"] = None

        return checkpoints

    if isinstance(weather_results, dict):
        weather_results = [weather_results]

    if not isinstance(weather_results, list) or len(weather_results) != len(
        checkpoints
    ):
        print("Weather response count does not match checkpoints.")

        for checkpoint in checkpoints:
            checkpoint["weather"] = None

        return checkpoints

    for checkpoint, forecast in zip(checkpoints, weather_results):
        checkpoint["weather"] = None

        if not isinstance(forecast, dict):
            continue

        hourly = forecast.get("hourly")

        if not isinstance(hourly, dict):
            continue

        hourly_times = hourly.get("time", [])

        if not hourly_times:
            continue

        arrival_time = datetime.fromisoformat(
            checkpoint["estimated_arrival"]
        ).astimezone(UTC)

        forecast_times = [
            datetime.fromisoformat(time).replace(tzinfo=UTC) for time in hourly_times
        ]

        closest_index = min(
            range(len(forecast_times)),
            key=lambda index: abs(
                (forecast_times[index] - arrival_time).total_seconds()
            ),
        )

        closest_time = forecast_times[closest_index]

        if abs((closest_time - arrival_time).total_seconds()) > 3600:
            continue

        required_variables = [
            "temperature_2m",
            "precipitation",
            "snowfall",
            "wind_speed_10m",
            "wind_gusts_10m",
            "weather_code",
        ]

        if any(
            not isinstance(hourly.get(variable), list)
            or len(hourly[variable]) <= closest_index
            for variable in required_variables
        ):
            continue

        checkpoint["weather"] = {
            "forecast_time": closest_time.isoformat(),
            "temperature_f": hourly["temperature_2m"][closest_index],
            "precipitation_mm": hourly["precipitation"][closest_index],
            "snowfall_cm": hourly["snowfall"][closest_index],
            "wind_speed_mph": hourly["wind_speed_10m"][closest_index],
            "wind_gusts_mph": hourly["wind_gusts_10m"][closest_index],
            "weather_code": hourly["weather_code"][closest_index],
        }

    return checkpoints
