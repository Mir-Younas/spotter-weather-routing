# Weather-Aware Truck Routing

A Django REST API that compares truck routes using forecast weather conditions. It evaluates weather risk at route checkpoints, recommends a lower-risk route, and provides a 48-hour weather-risk heatmap for route planning.

## Features

- Geocode origin and destination locations.
- Retrieve truck route alternatives using OpenRouteService.
- Generate route checkpoints at 10, 25, or 50-mile intervals.
- Match weather forecasts to estimated checkpoint arrival times.
- Assess wind, gusts, rain, snow, and load-related risk.
- Rank route alternatives by weather risk.
- Provide hourly corridor risk data for the next 48 hours.
- Validate API requests and return clear errors for invalid input.

## Request Validation

Django REST Framework serializers validate route-analysis inputs, including locations, departure time, load weight, and checkpoint interval. The heatmap endpoint validates timestamps and checkpoint data. Invalid requests return HTTP `400 Bad Request` responses.

## Tech Stack

- Python 3.13
- Django and Django REST Framework
- SQLite
- OpenRouteService
- Open-Meteo
- Requests and python-dotenv

## Getting Started

From the `backend` directory, create and activate a virtual environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file and configure the OpenRouteService API key and other environment variables required by the project settings.

Start the server:

```powershell
python manage.py migrate
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/` by default.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/routes/analyze/` | Compare truck route alternatives and weather risks. |
| POST | `/api/routes/heatmap/` | Retrieve hourly weather-risk data along a corridor for 48 hours. |

### Heatmap Request Example

```json
{
  "departure_time": "2026-10-16T08:00:00-05:00",
  "load_weight": 45000,
  "checkpoints": [
    { "latitude": 41.8781, "longitude": -87.6298, "mile_marker": 0 },
    { "latitude": 39.7817, "longitude": -89.6501, "mile_marker": 200 },
    { "latitude": 32.7767, "longitude": -96.7970, "mile_marker": 900 }
  ]
}
```

## Tests and Code Quality

Run Django system checks and automated tests:

```powershell
python manage.py check
python manage.py test routing
```

Check Python syntax:

```powershell
python -m compileall -q config routing
```

Install Ruff:

```powershell
python -m pip install ruff
```

Check linting and formatting:

```powershell
python -m ruff check .
python -m ruff format --check .
```

Automatically fix supported lint errors and format code:

```powershell
python -m ruff check . --fix
python -m ruff format .
```

## Project Status

The backend MVP is implemented. All 20 automated API tests pass, Ruff reports no lint errors, and all 26 checked Python files meet formatting requirements. A React frontend is planned. Route-ranking accuracy and all weather-risk thresholds have not yet been comprehensively tested.

## Notes

Forecast availability depends on the weather provider's forecast horizon. Weather-risk scores are planning guidance and should not replace official road advisories or safety requirements.
