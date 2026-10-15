from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase


class RouteAnalysisValidationTests(APITestCase):
    URL = "/api/routes/analyze/"

    def setUp(self):
        self.valid_payload = {
            "origin": "Chicago, IL",
            "destination": "Indianapolis, IN",
            "departure_time": "2026-10-16T08:00:00Z",
            "load_weight": 20000,
            "checkpoint_interval": 25,
        }

    @patch("routing.services.routing_service.geocode_location")
    def test_invalid_origin_returns_400(self, mock_geocode):
        mock_geocode.side_effect = ValueError("Location not found: xyznotarealcity123")

        payload = {
            **self.valid_payload,
            "origin": "xyznotarealcity123",
        }

        response = self.client.post(self.URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Location not found: xyznotarealcity123",
        )

    @patch("routing.services.routing_service.geocode_location")
    def test_invalid_destination_returns_400(self, mock_geocode):
        mock_geocode.side_effect = [
            (41.8781, -87.6298),
            ValueError("Location not found: xyznotarealcity123"),
        ]

        payload = {
            **self.valid_payload,
            "destination": "xyznotarealcity123",
        }

        response = self.client.post(self.URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Location not found: xyznotarealcity123",
        )
