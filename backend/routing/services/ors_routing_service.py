import math

import requests
from django.conf import settings

ORS_DIRECTIONS_URL = (
    "https://api.openrouteservice.org/v2/directions/driving-hgv/geojson"
)

ORS_SNAP_URL = "https://api.openrouteservice.org/v2/snap/driving-hgv"


def request_truck_route(coordinates):
    response = requests.post(
        ORS_DIRECTIONS_URL,
        json={"coordinates": coordinates},
        headers={
            "Authorization": settings.ORS_API_KEY,
            "Content-Type": "application/json",
        },
        timeout=45,
    )

    response.raise_for_status()
    return response.json()


def snap_to_road(coordinate):
    response = requests.post(
        ORS_SNAP_URL,
        json={
            "locations": [coordinate],
            "radius": 10000,
        },
        headers={
            "Authorization": settings.ORS_API_KEY,
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    response.raise_for_status()

    locations = response.json().get("locations", [])

    if not locations or locations[0] is None:
        return None

    return locations[0]["location"]


def generate_candidate_waypoints(coordinates):
    if len(coordinates) < 4:
        return []

    midpoint = coordinates[len(coordinates) // 2]

    previous_point = coordinates[max(0, len(coordinates) // 2 - 20)]

    next_point = coordinates[min(len(coordinates) - 1, len(coordinates) // 2 + 20)]

    longitude_scale = max(
        abs(math.cos(math.radians(midpoint[1]))),
        0.1,
    )

    delta_x = (next_point[0] - previous_point[0]) * longitude_scale

    delta_y = next_point[1] - previous_point[1]

    magnitude = math.hypot(delta_x, delta_y)

    if magnitude == 0:
        return []

    perpendicular_x = -delta_y / magnitude
    perpendicular_y = delta_x / magnitude

    candidates = []

    for direction in [1, -1]:
        offset = 0.5

        longitude = (
            midpoint[0] + (direction * perpendicular_x * offset) / longitude_scale
        )

        latitude = midpoint[1] + (direction * perpendicular_y * offset)

        if -180 <= longitude <= 180 and -90 <= latitude <= 90:
            candidates.append([longitude, latitude])

    return candidates


def sample_route_coordinates(coordinates, sample_count=20):
    if len(coordinates) < 2:
        return coordinates

    return [
        coordinates[round(index * (len(coordinates) - 1) / (sample_count - 1))]
        for index in range(sample_count)
    ]


def routes_are_similar(first_route, second_route):
    first_summary = first_route["properties"]["summary"]
    second_summary = second_route["properties"]["summary"]

    first_distance = first_summary["distance"]
    second_distance = second_summary["distance"]

    if first_distance == 0:
        return False

    distance_difference = abs(first_distance - second_distance) / first_distance

    if distance_difference > 0.01:
        return False

    first_points = sample_route_coordinates(first_route["geometry"]["coordinates"])

    second_points = sample_route_coordinates(second_route["geometry"]["coordinates"])

    matching_points = sum(
        1
        for first_point, second_point in zip(
            first_points,
            second_points,
        )
        if (
            abs(first_point[0] - second_point[0]) < 0.01
            and abs(first_point[1] - second_point[1]) < 0.01
        )
    )

    return matching_points / len(first_points) >= 0.9


def fetch_truck_routes(origin, destination):
    primary_result = request_truck_route([origin, destination])

    routes = primary_result.get("features", [])

    if not routes:
        return {
            "type": "FeatureCollection",
            "features": [],
        }

    primary_coordinates = routes[0]["geometry"]["coordinates"]

    candidates = generate_candidate_waypoints(primary_coordinates)

    for candidate in candidates:
        try:
            waypoint = snap_to_road(candidate)

            if waypoint is None:
                continue

            alternative_result = request_truck_route([origin, waypoint, destination])

            for feature in alternative_result.get("features", []):
                is_duplicate = any(
                    routes_are_similar(feature, existing) for existing in routes
                )

                if not is_duplicate:
                    routes.append(feature)

        except requests.RequestException:
            print(f"Alternative route unavailable for candidate {candidate}")

    return {
        "type": "FeatureCollection",
        "features": routes,
    }
