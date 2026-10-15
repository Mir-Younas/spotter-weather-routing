from django.urls import path

from .heatmap_views import heatmap_view
from .views import analyze_routes

urlpatterns = [
    path("analyze/", analyze_routes),
    path("heatmap/", heatmap_view),
]
