from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import RouteAnalysisSerializer
from .services.routing_service import analyze_routes_service


@api_view(["POST"])
def analyze_routes(request):
    serializer = RouteAnalysisSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    result = analyze_routes_service(serializer.validated_data)

    return Response(result)
