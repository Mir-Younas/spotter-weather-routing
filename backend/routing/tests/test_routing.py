from django.test import TestCase
from django.urls import resolve
from rest_framework.test import APIClient

from routing.views import analyze_routes


class RoutingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/routes/analyze/"

    def test_analyze_url_resolves(self):
        match = resolve(self.url)

        self.assertEqual(
            match.func.cls if hasattr(match.func, "cls") else match.func,
            analyze_routes.cls if hasattr(analyze_routes, "cls") else analyze_routes,
        )

    def test_analyze_rejects_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)

    def test_analyze_rejects_empty_payload(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_analyze_rejects_invalid_json(self):
        response = self.client.generic(
            "POST",
            self.url,
            data='{"origin":',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_analyze_rejects_json_array(self):
        response = self.client.post(
            self.url,
            ["Chicago", "Dallas"],
            format="json",
        )

        self.assertIn(response.status_code, [400, 422])

    def test_analyze_rejects_missing_destination(self):
        response = self.client.post(
            self.url,
            {"origin": "Chicago, IL"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
