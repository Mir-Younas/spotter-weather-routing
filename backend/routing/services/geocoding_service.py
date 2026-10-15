import requests
from django.conf import settings

ORS_GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"


def geocode_location(location: str):
    response = requests.get(
        ORS_GEOCODE_URL,
        params={
            "api_key": settings.ORS_API_KEY,
            "text": location,
            "size": 1,
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()
    features = data.get("features", [])

    if not features:
        raise ValueError(f"Location not found: {location}")

    return features[0]["geometry"]["coordinates"]
