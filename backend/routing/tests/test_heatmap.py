from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient


class HeatmapAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/routes/heatmap/"
        self.payload = {
            "departure_time": "2026-10-16T08:00:00-05:00",
            "load_weight": 45000,
            "checkpoints": [
                {
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                    "mile_marker": 0,
                },
                {
                    "latitude": 39.7817,
                    "longitude": -89.6501,
                    "mile_marker": 200,
                },
            ],
        }

    @patch("routing.heatmap_views.build_heatmap")
    def test_heatmap_success(self, mock_build_heatmap):
        mock_build_heatmap.return_value = {
            "start_time": "2026-10-16T13:00:00+00:00",
            "end_time": "2026-10-18T13:00:00+00:00",
            "slider_hours": list(range(49)),
            "locations": [],
        }

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["slider_hours"]), 49)
        self.assertEqual(response.data["slider_hours"][0], 0)
        self.assertEqual(response.data["slider_hours"][-1], 48)

        mock_build_heatmap.assert_called_once()
        kwargs = mock_build_heatmap.call_args.kwargs

        self.assertEqual(kwargs["load_weight"], 45000)
        self.assertEqual(kwargs["checkpoints"], self.payload["checkpoints"])
        self.assertIsNotNone(kwargs["start_time"].tzinfo)

    def test_missing_checkpoints(self):
        payload = self.payload.copy()
        payload.pop("checkpoints")

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_empty_checkpoints(self):
        payload = {**self.payload, "checkpoints": []}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_missing_departure_time(self):
        payload = self.payload.copy()
        payload.pop("departure_time")

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_invalid_departure_time(self):
        payload = {**self.payload, "departure_time": "invalid-date"}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_departure_time_without_timezone(self):
        payload = {
            **self.payload,
            "departure_time": "2026-10-16T08:00:00",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_missing_load_weight(self):
        payload = self.payload.copy()
        payload.pop("load_weight")

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_invalid_load_weight(self):
        for weight in [-1, 80001, "heavy", True]:
            with self.subTest(weight=weight):
                payload = {**self.payload, "load_weight": weight}

                response = self.client.post(self.url, payload, format="json")

                self.assertEqual(response.status_code, 400)

    def test_invalid_latitude(self):
        payload = {
            **self.payload,
            "checkpoints": [
                {
                    "latitude": 100,
                    "longitude": -87.6298,
                    "mile_marker": 0,
                }
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_invalid_longitude(self):
        payload = {
            **self.payload,
            "checkpoints": [
                {
                    "latitude": 41.8781,
                    "longitude": -200,
                    "mile_marker": 0,
                }
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_negative_mile_marker(self):
        payload = {
            **self.payload,
            "checkpoints": [
                {
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                    "mile_marker": -10,
                }
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_too_many_checkpoints(self):
        payload = {
            **self.payload,
            "checkpoints": [
                {
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                    "mile_marker": i,
                }
                for i in range(201)
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    @patch("routing.heatmap_views.build_heatmap")
    def test_service_validation_error(self, mock_build_heatmap):
        mock_build_heatmap.side_effect = ValueError("Forecast window is unavailable.")

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    @patch("routing.heatmap_views.build_heatmap")
    def test_service_failure(self, mock_build_heatmap):
        mock_build_heatmap.side_effect = RuntimeError("Weather provider unavailable")

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 503)
        self.assertIn("error", response.data)
