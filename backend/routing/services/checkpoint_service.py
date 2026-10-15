from datetime import timedelta
from math import atan2, cos, radians, sin, sqrt

EARTH_RADIUS_MILES = 3958.7613


def haversine_distance(point1, point2):
    lon1, lat1 = point1
    lon2, lat2 = point2

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2

    return 2 * EARTH_RADIUS_MILES * atan2(sqrt(a), sqrt(max(0, 1 - a)))


def generate_checkpoints(
    coordinates,
    interval_miles,
    departure_time,
    duration_hours,
    route_distance_miles,
):
    if len(coordinates) < 2:
        raise ValueError("Route must contain at least two coordinates.")

    if interval_miles <= 0:
        raise ValueError("Checkpoint interval must be positive.")

    if route_distance_miles <= 0:
        raise ValueError("Route distance must be positive.")

    segment_distances = []

    for index in range(1, len(coordinates)):
        distance = haversine_distance(
            coordinates[index - 1],
            coordinates[index],
        )

        segment_distances.append(distance)

    polyline_distance = sum(segment_distances)

    if polyline_distance <= 0:
        raise ValueError("Route geometry has no measurable distance.")

    # Align checkpoint mileage with the routing API's
    # reported road distance.
    distance_scale = route_distance_miles / polyline_distance

    checkpoints = []

    def create_checkpoint(point, mile_marker):
        progress = mile_marker / route_distance_miles

        arrival_time = departure_time + timedelta(hours=duration_hours * progress)

        return {
            "mile_marker": round(mile_marker, 2),
            "latitude": round(point[1], 6),
            "longitude": round(point[0], 6),
            "estimated_arrival": arrival_time.isoformat(),
            "weather": None,
            "risk_score": None,
        }

    checkpoints.append(create_checkpoint(coordinates[0], 0))

    accumulated_distance = 0.0
    next_checkpoint = float(interval_miles)

    for index, segment_distance in enumerate(
        segment_distances,
        start=1,
    ):
        if segment_distance <= 0:
            continue

        start = coordinates[index - 1]
        end = coordinates[index]

        scaled_segment_distance = segment_distance * distance_scale

        segment_end_distance = accumulated_distance + scaled_segment_distance

        while (
            next_checkpoint < route_distance_miles
            and next_checkpoint <= segment_end_distance
        ):
            fraction = (
                next_checkpoint - accumulated_distance
            ) / scaled_segment_distance

            fraction = max(
                0.0,
                min(fraction, 1.0),
            )

            longitude = start[0] + fraction * (end[0] - start[0])

            latitude = start[1] + fraction * (end[1] - start[1])

            checkpoints.append(
                create_checkpoint(
                    [longitude, latitude],
                    next_checkpoint,
                )
            )

            next_checkpoint += interval_miles

        accumulated_distance = segment_end_distance

    checkpoints.append(
        create_checkpoint(
            coordinates[-1],
            route_distance_miles,
        )
    )

    return checkpoints
