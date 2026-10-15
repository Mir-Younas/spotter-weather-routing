import logging
import math
from datetime import datetime

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.heatmap_service import build_heatmap

logger = logging.getLogger(__name__)


@api_view(["POST"])
def heatmap_view(request):
    checkpoints = request.data.get("checkpoints")
    departure_time = request.data.get("departure_time")
    load_weight = request.data.get("load_weight")

    if not isinstance(checkpoints, list) or not checkpoints:
        return Response(
            {"error": "A non-empty checkpoints list is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(departure_time, str):
        return Response(
            {"error": "A valid departure_time is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        parsed_departure_time = datetime.fromisoformat(departure_time)

        if parsed_departure_time.tzinfo is None:
            raise ValueError("Departure time must include a timezone.")

    except ValueError:
        return Response(
            {"error": ("Invalid departure_time. Use ISO 8601 format with a timezone.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if (
        not isinstance(load_weight, (int, float))
        or isinstance(load_weight, bool)
        or not math.isfinite(load_weight)
        or not 0 <= load_weight <= 80000
    ):
        return Response(
            {"error": ("load_weight must be a number between 0 and 80000 pounds.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(checkpoints) > 200:
        return Response(
            {"error": "Maximum 200 checkpoints allowed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    for index, checkpoint in enumerate(checkpoints):
        if not isinstance(checkpoint, dict):
            return Response(
                {"error": (f"Checkpoint {index + 1} must be an object.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for field in ("latitude", "longitude", "mile_marker"):
            value = checkpoint.get(field)

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
            ):
                return Response(
                    {"error": (f"Checkpoint {index + 1} has an invalid {field}.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        latitude = checkpoint["latitude"]
        longitude = checkpoint["longitude"]
        mile_marker = checkpoint["mile_marker"]

        if not -90 <= latitude <= 90:
            return Response(
                {"error": (f"Checkpoint {index + 1} has an invalid latitude.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not -180 <= longitude <= 180:
            return Response(
                {"error": (f"Checkpoint {index + 1} has an invalid longitude.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if mile_marker < 0:
            return Response(
                {"error": (f"Checkpoint {index + 1} has an invalid mile_marker.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

    try:
        result = build_heatmap(
            checkpoints=checkpoints,
            start_time=parsed_departure_time,
            load_weight=load_weight,
        )

    except ValueError as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as error:
        logger.exception("Failed to generate weather heatmap")

        return Response(
            {
                "error": "Unable to generate weather heatmap.",
                "detail": str(error),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(
        result,
        status=status.HTTP_200_OK,
    )
