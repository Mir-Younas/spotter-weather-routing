# Weather-Aware Truck Routing — Backend

A Django REST API for weather-aware truck route planning. The backend retrieves alternative truck routes, evaluates forecast weather conditions at route checkpoints, compares weather-related risks, and recommends a lower-risk eligible route.

It also provides a 48-hour weather-risk heatmap to help users understand how conditions may change along a selected route.

## Features

- Geocode origin and destination locations.
- Retrieve alternative truck routes using OpenRouteService.
- Generate route checkpoints at 10, 25, or 50-mile intervals.
- Estimate truck arrival times at individual checkpoints.
- Retrieve forecast weather data using Open-Meteo.
- Evaluate temperature, wind, gusts, precipitation, snowfall, and load-related weather risk.
- Calculate route-level risk summaries.
- Compare alternative routes based on weather risk and journey duration.
- Recommend an eligible route based on the route-ranking logic.
- Generate a 48-hour hourly weather-risk heatmap.
- Validate incoming API requests.
- Return meaningful HTTP 400 responses for invalid locations and input data.
- Handle weather-provider failures in the heatmap API.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13 | Backend programming language |
| Django 6.1 | Web framework |
| Django REST Framework | REST API development |
| SQLite | Development database |
| OpenRouteService | Geocoding and route alternatives |
| Open-Meteo | Weather forecasts |
| Requests | External HTTP requests |
| python-dotenv | Environment variable management |
| django-cors-headers | Cross-origin request handling |
| Ruff | Python linting and formatting |

## Project Structure

```text
backend/
├── config/
│   ├── settings.py
│   └── urls.py
├── routing/
│   ├── services/
│   │   ├── geocoding_service.py
│   │   ├── ors_routing_service.py
│   │   ├── checkpoint_service.py
│   │   ├── weather_service.py
│   │   ├── risk_scoring_service.py
│   │   ├── routing_service.py
│   │   └── heatmap_service.py
│   ├── tests/
│   ├── serializers.py
│   ├── views.py
│   ├── heatmap_views.py
│   └── urls.py
├── .env.example
├── requirements.txt
├── manage.py
└── README.md
```

## Getting Started

### 1. Create a virtual environment

From the `backend` directory:

```powershell
py -3.13 -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the backend directory using the project's `.env.example` as a reference.

Configure the required environment variables, including your OpenRouteService API key.

```env
ORS_API_KEY=your_openrouteservice_api_key
```

Do not commit `.env` files or API keys to version control.

### 4. Run database migrations

```powershell
python manage.py migrate
```

### 5. Start the development server

```powershell
python manage.py runserver
```

The backend runs at:

`http://127.0.0.1:8000/`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/routes/analyze/` | Analyze and compare alternative truck routes |
| POST | `/api/routes/heatmap/` | Generate a 48-hour weather-risk heatmap |

### Route Analysis

**Endpoint**

`POST /api/routes/analyze/`

**Example request**

```json
{
  "origin": "Chicago, IL",
  "destination": "Indianapolis, IN",
  "departure_time": "2026-10-16T08:00:00-05:00",
  "load_weight": 20000,
  "checkpoint_interval": 25
}
```

**Request fields**

| Field | Type | Description |
|---|---|---|
| `origin` | string | Starting location |
| `destination` | string | Destination location |
| `departure_time` | ISO 8601 datetime | Planned departure time |
| `load_weight` | number | Truck load weight in pounds |
| `checkpoint_interval` | integer | Checkpoint spacing: 10, 25, or 50 miles |

The response contains analyzed route alternatives, checkpoint weather information, route-level risk summaries, and the recommended route identifier when an eligible recommendation is available.

A recommendation may be unavailable if the alternatives fail the backend's eligibility criteria.

### Weather Heatmap

**Endpoint**

`POST /api/routes/heatmap/`

**Example request**

```json
{
  "departure_time": "2026-10-16T08:00:00-05:00",
  "load_weight": 20000,
  "checkpoints": [
    {
      "latitude": 41.8781,
      "longitude": -87.6298,
      "mile_marker": 0
    },
    {
      "latitude": 41.5,
      "longitude": -87.0,
      "mile_marker": 50
    },
    {
      "latitude": 39.7684,
      "longitude": -86.1581,
      "mile_marker": 186
    }
  ]
}
```

**Response structure**

```json
{
  "start_time": "ISO 8601 datetime",
  "end_time": "ISO 8601 datetime",
  "slider_hours": [0, 1, 2, 3],
  "locations": [
    {
      "mile_marker": 0,
      "latitude": 41.8781,
      "longitude": -87.6298,
      "hours": [
        {
          "offset_hours": 0,
          "risk_level": "MODERATE",
          "risk_score": 25,
          "temperature_f": 50,
          "wind_speed_mph": 12,
          "wind_gusts_mph": 20,
          "precipitation_mm": 0,
          "snowfall_cm": 0
        }
      ]
    }
  ]
}
```

*The response above is an abbreviated structural illustration, not a live forecast. The actual response contains hourly forecast entries across the supported 48-hour period.*

For performance, the heatmap samples up to 20 locations along the route, even when the original route contains more checkpoints.

## Weather Risk Assessment

The backend evaluates weather conditions using factors such as:

- Wind speed and gusts
- Rainfall and precipitation
- Snowfall
- Temperature
- Truck load weight

Weather conditions are assessed at estimated checkpoint arrival times for route recommendations.

The application distinguishes between these risk levels:

| Risk level | Meaning |
|---|---|
| LOW | Lower estimated weather risk |
| MODERATE | Some weather risk |
| HIGH | Elevated weather risk |
| SEVERE | Severe weather risk |
| NO_TRAVEL | Conditions classified as unsuitable for travel |
| UNKNOWN | Insufficient weather information |

Route ranking considers weather risk, hazardous mileage, forecast availability, and travel duration.

**Important:** A recommended route is not necessarily free of weather hazards. Users should review the full forecast and official road advisories before travel.

## Request Validation and Error Handling

Django REST Framework serializers validate route-analysis requests.

The heatmap endpoint validates checkpoint coordinates, timestamps, and load weight.

Examples of invalid requests include:

- Missing origin or destination
- Invalid departure time
- Negative load weight
- Unsupported checkpoint interval
- Invalid checkpoint coordinates
- Unknown origin or destination

For an unknown location, the route-analysis endpoint returns HTTP 400.

**Example error response**

```json
{
  "detail": "Location not found: xyznotarealcity123"
}
```

The heatmap endpoint also handles weather-provider failures and returns an appropriate error response.

## Testing

Run Django system checks:

```powershell
python manage.py check
```

Run automated tests:

```powershell
python manage.py test
```

The test suite covers route analysis, weather heatmap behavior, request validation, error handling, and invalid-location scenarios.

**Latest verified results:**

- 22 automated tests passed.
- Django system checks passed.
- Ruff linting passed.
- Ruff formatting checks passed.

## Code Quality

Run Ruff linting:

```powershell
ruff check .
```

Verify formatting:

```powershell
ruff format --check .
```

Automatically format Python files:

```powershell
ruff format .
```

## Limitations

- Weather forecast availability depends on the external provider and forecast horizon.
- Risk calculations depend on the available forecast data and the application's configured scoring rules.
- Estimated checkpoint arrival times are based on route duration estimates, not live truck telemetry.
- The heatmap samples up to 20 route locations.
- Weather conditions can change after analysis.
- The application does not replace official road closures, regulatory restrictions, or professional dispatch decisions.
- Route-ranking accuracy and weather-risk thresholds have not been comprehensively validated against real-world outcomes.

## Project Status

The backend MVP is implemented and integrated with the React frontend.

The route-analysis and heatmap APIs have been exercised through the browser, and all 22 automated backend tests pass.

This project is intended as a weather-aware route-planning demonstration and should not be treated as a certified commercial trucking navigation or safety system.