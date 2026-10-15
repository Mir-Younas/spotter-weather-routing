from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import RouteAnalysisSerializer
from .services.routing_service import analyze_routes_service


@api_view(["POST"])
def analyze_routes(request):
    serializer = RouteAnalysisSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        result = analyze_routes_service(serializer.validated_data)
    except ValueError as exc:
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(result)
