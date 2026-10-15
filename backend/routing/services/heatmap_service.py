from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
VARIABLES = (
    "temperature_2m,precipitation,snowfall,wind_speed_10m,wind_gusts_10m,weather_code"
)
MAX_LOCATIONS = 20
BATCH_SIZE = 10


def build_heatmap(checkpoints, start_time, load_weight):
    """Return hourly risk points from start_time through start_time + 48 hours."""
    from .risk_scoring_service import calculate_weather_risk

    if not checkpoints:
        raise ValueError("At least one checkpoint is required.")

    # Keep the endpoints and spread the remaining locations across the corridor.
    count = min(MAX_LOCATIONS, len(checkpoints))
    indices = (
        sorted({round(i * (len(checkpoints) - 1) / (count - 1)) for i in range(count)})
        if count > 1
        else [0]
    )
    locations = [checkpoints[i] for i in indices]

    start_utc = start_time.astimezone(UTC)
    target_hours = [start_utc + timedelta(hours=i) for i in range(49)]
    last_date = target_hours[-1].date()
    days = (last_date - datetime.now(UTC).date()).days + 1
    if days < 1 or days > 16:
        raise ValueError(
            "The 48-hour forecast window must fall within the next 16 forecast days."
        )

    def fetch_batch(batch):
        params = {
            "latitude": ",".join(str(point["latitude"]) for point in batch),
            "longitude": ",".join(str(point["longitude"]) for point in batch),
            "hourly": VARIABLES,
            "timezone": "UTC",
            "forecast_days": days,
            "wind_speed_unit": "mph",
            "temperature_unit": "fahrenheit",
        }
        response = requests.get(OPEN_METEO_URL, params=params, timeout=25)
        response.raise_for_status()
        result = response.json()
        result = [result] if isinstance(result, dict) else result
        if not isinstance(result, list) or len(result) != len(batch):
            raise ValueError(
                "Weather provider returned an unexpected number of locations."
            )
        return result

    batches = [
        locations[i : i + BATCH_SIZE] for i in range(0, len(locations), BATCH_SIZE)
    ]
    with ThreadPoolExecutor(max_workers=min(3, len(batches))) as executor:
        results = list(executor.map(fetch_batch, batches))

    forecasts = [item for batch in results for item in batch]
    points = []
    for checkpoint, forecast in zip(locations, forecasts):
        hourly = forecast.get("hourly") or {}
        times = hourly.get("time") or []
        parsed_times = [
            datetime.fromisoformat(value).replace(tzinfo=UTC) for value in times
        ]
        location_hours = []
        for offset, target in enumerate(target_hours):
            if not parsed_times:
                break
            index = min(
                range(len(parsed_times)),
                key=lambda i: abs((parsed_times[i] - target).total_seconds()),
            )
            if abs((parsed_times[index] - target).total_seconds()) > 3600:
                location_hours.append(
                    {
                        "offset_hours": offset,
                        "risk_level": "UNKNOWN",
                        "risk_score": None,
                    }
                )
                continue
            fields = {
                "temperature_f": "temperature_2m",
                "precipitation_mm": "precipitation",
                "snowfall_cm": "snowfall",
                "wind_speed_mph": "wind_speed_10m",
                "wind_gusts_mph": "wind_gusts_10m",
                "weather_code": "weather_code",
            }
            weather = {}
            for output_name, input_name in fields.items():
                values = hourly.get(input_name)
                weather[output_name] = (
                    values[index]
                    if isinstance(values, list) and index < len(values)
                    else None
                )
            risk = calculate_weather_risk(weather, load_weight)
            location_hours.append(
                {
                    "offset_hours": offset,
                    "forecast_time": parsed_times[index].isoformat(),
                    "risk_level": risk["level"],
                    "risk_score": risk["score"],
                    "temperature_f": weather["temperature_f"],
                    "wind_speed_mph": weather["wind_speed_mph"],
                    "wind_gusts_mph": weather["wind_gusts_mph"],
                    "precipitation_mm": weather["precipitation_mm"],
                    "snowfall_cm": weather["snowfall_cm"],
                    "weather_code": weather["weather_code"],
                }
            )
        points.append(
            {
                "mile_marker": checkpoint.get("mile_marker"),
                "latitude": checkpoint["latitude"],
                "longitude": checkpoint["longitude"],
                "hours": location_hours,
            }
        )

    return {
        "start_time": start_utc.isoformat(),
        "end_time": target_hours[-1].isoformat(),
        "slider_hours": list(range(49)),
        "locations": points,
    }
