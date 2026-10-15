from .checkpoint_service import generate_checkpoints
from .geocoding_service import geocode_location
from .ors_routing_service import fetch_truck_routes
from .risk_scoring_service import score_route_checkpoints
from .weather_service import fetch_checkpoint_weather


def analyze_routes_service(data):
    origin_coordinates = geocode_location(data["origin"])

    destination_coordinates = geocode_location(data["destination"])

    routing_result = fetch_truck_routes(
        origin_coordinates,
        destination_coordinates,
    )

    routes = []

    for index, feature in enumerate(
        routing_result["features"],
        start=1,
    ):
        summary = feature["properties"]["summary"]

        distance_miles = summary["distance"] / 1609.344

        duration_hours = summary["duration"] / 3600

        coordinates = feature["geometry"]["coordinates"]

        checkpoints = generate_checkpoints(
            coordinates=coordinates,
            interval_miles=data["checkpoint_interval"],
            departure_time=data["departure_time"],
            duration_hours=duration_hours,
            route_distance_miles=distance_miles,
        )

        checkpoints = fetch_checkpoint_weather(checkpoints)

        risk_summary = score_route_checkpoints(
            checkpoints,
            data["load_weight"],
        )

        routes.append(
            {
                "id": index,
                "distance_miles": round(distance_miles, 2),
                "duration_hours": round(duration_hours, 2),
                "geometry": feature["geometry"],
                "checkpoints": checkpoints,
                "risk_summary": risk_summary,
            }
        )

    # Do not recommend routes containing
    # NO_TRAVEL conditions or missing forecasts.
    eligible_routes = [
        route
        for route in routes
        if (
            route["risk_summary"]["unavailable_checkpoints"] == 0
            and route["risk_summary"]["no_travel_miles"] == 0
            and route["risk_summary"]["average_risk_score"] is not None
        )
    ]

    recommended_route = None

    if eligible_routes:
        safest_route = min(
            eligible_routes,
            key=lambda route: (
                route["risk_summary"]["severe_miles"],
                route["risk_summary"]["high_miles"],
                route["risk_summary"]["average_risk_score"],
                route["duration_hours"],
            ),
        )

        recommended_route = safest_route["id"]

    return {
        "origin": data["origin"],
        "destination": data["destination"],
        "departure_time": data["departure_time"].isoformat(),
        "load_weight": data["load_weight"],
        "checkpoint_interval": data["checkpoint_interval"],
        "routes": routes,
        "recommended_route": recommended_route,
    }
