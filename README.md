# Weather-Aware Truck Routing

**A full-stack truck route planning application that evaluates forecast weather conditions, compares alternative routes, and recommends lower-risk routes.**

Built with **Django REST Framework, React, TypeScript, OpenRouteService, and Open-Meteo**.

The application helps drivers and dispatchers assess weather-related risks before starting a journey. Instead of comparing routes based only on distance or travel time, it evaluates forecast conditions at estimated checkpoint arrival times.

## Overview

Weather conditions can vary significantly across long-distance trucking routes. High winds, heavy rainfall, snowfall, and other hazardous conditions may affect travel safety.

Weather-Aware Truck Routing combines routing information with weather forecasts to help users:

- Compare multiple truck route alternatives.
- Understand potential weather hazards along each route.
- Identify lower-risk route options.
- Explore how weather risks change over the next 48 hours.
- Make more informed route-planning decisions.

**The application is a planning aid, not a replacement for official weather warnings, road advisories, or professional dispatch decisions.**

## Key Features

### 1. Truck Route Planning

- Enter an origin and destination.
- Choose a planned departure date and time.
- Specify truck load weight.
- Select checkpoint intervals of 10, 25, or 50 miles.
- Retrieve alternative routes through OpenRouteService.

### 2. Weather-Aware Route Analysis

- Generate checkpoints along alternative routes.
- Estimate arrival times at individual checkpoints.
- Retrieve forecast conditions using Open-Meteo.
- Evaluate wind, gusts, precipitation, snowfall, temperature, and load-related risk.
- Calculate route-level risk summaries.
- Compare routes based on hazardous mileage, average risk, and estimated duration.
- Recommend a lower-risk eligible route when available.

### 3. Interactive Route Map

- Display alternative routes using Leaflet.
- Highlight the recommended route in green.
- Highlight the currently selected route in blue.
- Display remaining alternatives in gray.
- Switch between routes to inspect their weather conditions.

### 4. Route Comparison Dashboard

Compare route alternatives using:

- Total distance
- Estimated travel duration
- Average weather-risk score
- Number of checkpoints
- High-risk mileage
- Severe-risk mileage
- No-travel mileage
- Missing weather forecasts

The dashboard also displays warnings when a route contains hazardous weather conditions.

### 5. 48-Hour Weather Risk Heatmap

- Explore hourly weather-risk forecasts over a 48-hour window.
- View risk levels across sampled route checkpoints.
- Navigate forecast hours using an interactive slider.
- Inspect detailed weather conditions for individual locations and times.
- Visualize estimated truck arrival times against the forecast timeline.
- Analyze up to 20 sampled locations per heatmap request.

### 6. Input Validation and Error Handling

- Validate route-planning form inputs.
- Reject unsupported checkpoint intervals and invalid load weights.
- Return meaningful errors for unknown locations.
- Handle unavailable weather data.
- Display backend validation errors in the frontend.

## Technology Stack

### Backend

| Technology | Purpose |
|---|---|
| Python 3.13 | Programming language |
| Django | Backend framework |
| Django REST Framework | REST API |
| SQLite | Development database |
| OpenRouteService | Geocoding and route alternatives |
| Open-Meteo | Weather forecasts |
| Requests | HTTP requests |
| python-dotenv | Environment configuration |
| django-cors-headers | Cross-origin API access |
| Ruff | Linting and formatting |

### Frontend

| Technology | Purpose |
|---|---|
| React | User interface |
| TypeScript | Type safety |
| Vite | Development and production builds |
| Tailwind CSS v4 | Styling |
| Axios | API communication |
| Leaflet | Interactive mapping |
| React Leaflet | React map components |
| Lucide React | Interface icons |
| ESLint | Code quality |

## System Architecture

```text
                         USER
                           |
                           v
                React + TypeScript
                   Frontend
                           |
                           v
                    Axios Client
                           |
                           v
                 Django REST API
                           |
              +------------+------------+
              |                         |
              v                         v
       Route Analysis              Weather Heatmap
              |                         |
              v                         v
       OpenRouteService            Route Checkpoints
              |                         |
              v                         v
       Route Alternatives          Open-Meteo API
              |                         |
              v                         v
       Route Checkpoints           Hourly Forecasts
              |                         |
              v                         v
        Open-Meteo API             Risk Assessment
              |
              v
        Risk Assessment
              |
              v
       Route Comparison
              |
              v
       Route Recommendation
```

### How It Works

1. The user enters route-planning details in the React dashboard.
2. The frontend submits a route-analysis request to Django.
3. The backend geocodes the origin and destination.
4. OpenRouteService provides alternative truck routes.
5. Checkpoints are generated along each route.
6. The backend estimates when the truck will reach each checkpoint.
7. Open-Meteo provides forecast weather information.
8. Weather-risk scores are calculated for the checkpoints.
9. Route alternatives are compared and a lower-risk eligible route is recommended when available.
10. The user can select a route and explore its 48-hour weather-risk heatmap.

## Project Structure

```text
spotter-weather-routing/
├── backend/
│   ├── config/
│   ├── routing/
│   │   ├── services/
│   │   ├── tests/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── heatmap_views.py
│   │   └── urls.py
│   ├── manage.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── map/
│   │   │   ├── routing/
│   │   │   └── weather/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── README.md
│
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.13
- Node.js and npm
- Git
- An OpenRouteService API key
- Internet access for routing and weather services

### 1. Clone the Repository

```bash
git clone https://github.com/Mir-Younas/spotter-weather-routing.git
cd spotter-weather-routing
```

### 2. Set Up the Backend

Navigate to the backend directory:

```powershell
cd backend
```

Create a Python virtual environment:

```powershell
py -3.13 -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file in `backend/` and configure the environment variables required by the Django settings.

At minimum, configure the OpenRouteService API key:

```env
ORS_API_KEY=your_openrouteservice_api_key
```

Apply database migrations:

```powershell
python manage.py migrate
```

Start the Django development server:

```powershell
python manage.py runserver
```

The backend will be available at:

`http://127.0.0.1:8000/`

### 3. Set Up the Frontend

Open a second terminal and navigate to the frontend directory:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

Start the development server:

```powershell
npm run dev
```

Open the URL displayed by Vite, usually:

`http://localhost:5173/`

Both the Django backend and React frontend must be running for the application to work locally.

## API Documentation

The backend exposes two primary REST endpoints.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/routes/analyze/` | Analyze and compare truck route alternatives |
| POST | `/api/routes/heatmap/` | Retrieve hourly weather-risk data for route checkpoints |

### Route Analysis Example

**Request**

```http
POST /api/routes/analyze/
Content-Type: application/json
```

```json
{
  "origin": "Chicago, IL",
  "destination": "Indianapolis, IN",
  "departure_time": "2026-10-16T08:00:00-05:00",
  "load_weight": 20000,
  "checkpoint_interval": 25
}
```

The response includes analyzed route alternatives, checkpoint weather assessments, route-level risk information, and a recommended route identifier when available.

### Heatmap Example

**Request**

```http
POST /api/routes/heatmap/
Content-Type: application/json
```

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
      "latitude": 39.7684,
      "longitude": -86.1581,
      "mile_marker": 186
    }
  ]
}
```

The response contains hourly weather-risk information for the selected route checkpoints, including risk scores, risk levels, and available forecast measurements.

For additional details, see:

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)

## Weather Risk Assessment

The application considers several weather-related factors, including wind speed, wind gusts, rainfall, snowfall, temperature, and truck load weight.

Risk levels are categorized as:

| Level | Description |
|---|---|
| LOW | Lower estimated weather risk |
| MODERATE | Moderate weather risk |
| HIGH | Elevated weather risk |
| SEVERE | Severe weather risk |
| NO_TRAVEL | Conditions classified as unsuitable for travel |
| UNKNOWN | Insufficient forecast information |

Route comparison considers hazardous mileage, average risk, forecast coverage, and estimated travel duration.

**A recommended route is not guaranteed to be safe.** Users should review weather advisories, road conditions, and applicable trucking regulations before traveling.

## Testing and Code Quality

### Backend

From the `backend` directory:

Run Django system checks:

```powershell
python manage.py check
```

Run automated tests:

```powershell
python manage.py test
```

Run Ruff linting:

```powershell
ruff check .
```

Verify code formatting:

```powershell
ruff format --check .
```

**Latest verified backend results:**

- 22 automated tests passed.
- Django system checks passed.
- Ruff linting passed.
- Ruff formatting passed.

### Frontend

From the `frontend` directory:

Run ESLint:

```powershell
npm run lint
```

Compile TypeScript and build for production:

```powershell
npm run build
```

**Latest verified frontend results:**

- ESLint passed without errors.
- TypeScript compilation passed.
- Vite production build completed successfully.

## Current Limitations

- Route and weather information depend on third-party API availability.
- Forecast accuracy varies by location and forecast horizon.
- Route recommendations use estimated checkpoint arrival times rather than live vehicle tracking.
- Actual travel times may change due to traffic, stops, road closures, or operational delays.
- Heatmap visualization is limited to a maximum of 20 sampled route locations.
- Missing weather forecasts may reduce the completeness of risk assessments.
- The risk-scoring system has not been comprehensively validated against real-world trucking outcomes.
- The application is not a certified commercial navigation or weather-safety system.

## Project Status

**Full-stack MVP implemented.**

The application includes a working Django REST API and React dashboard with route planning, alternative-route comparison, interactive mapping, weather-risk assessment, and a 48-hour weather heatmap.

The backend currently passes 22 automated tests, and the frontend passes ESLint, TypeScript compilation, and production-build checks.

## Author

**Mir Younas**

GitHub: [Mir-Younas](https://github.com/Mir-Younas)

Project Repository: [Weather-Aware Truck Routing](https://github.com/Mir-Younas/spotter-weather-routing)

## License

This project is publicly available for demonstration and technical assessment purposes.

No open-source license has been assigned to this repository. All rights are reserved by the author.