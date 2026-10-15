# Weather-Aware Truck Routing — Frontend

A responsive React and TypeScript dashboard for weather-aware truck route planning.

The frontend allows users to compare alternative truck routes, visualize weather-related risks on an interactive map, and explore a 48-hour weather-risk heatmap.

It communicates with a Django REST API that provides route alternatives, weather forecasts, checkpoint risk assessments, and route recommendations.

## Features

### Route Planning

- Enter origin and destination locations.
- Select a planned departure date and time.
- Specify truck load weight in pounds.
- Choose checkpoint intervals of 10, 25, or 50 miles.
- Submit route-analysis requests to the backend.
- Display loading states and API validation errors.

### Interactive Route Map

- Visualize alternative truck routes using Leaflet.
- Highlight the selected route in blue.
- Highlight the recommended route in green.
- Display other alternatives in gray.
- Explore routes using interactive map controls.
- Switch between alternatives to inspect their weather-risk information.

### Route Comparison

- Compare route distances and estimated durations.
- View average weather-risk scores.
- Inspect checkpoint counts.
- Compare high-risk, severe-risk, and no-travel mileage.
- Identify the recommended route.
- Display warnings when hazardous conditions are present.
- Indicate when forecast information is unavailable.

### 48-Hour Weather Heatmap

- Display hourly weather-risk forecasts along the selected route.
- Visualize risk levels using color-coded cells.
- Explore forecast hours with a time slider.
- View detailed weather information for individual checkpoints.
- Inspect temperature, wind speed, gusts, precipitation, and snowfall.
- Highlight estimated truck arrival times at route checkpoints.
- Support up to 20 sampled locations along the selected route.

### Responsive Dashboard

- Responsive layout for desktop and smaller screens.
- Organized route-planning, route-comparison, map, and weather sections.
- Consistent interface styling using Tailwind CSS.
- Lucide icons for navigation and visual indicators.

## Technology Stack

| Technology | Purpose |
|---|---|
| React | User interface |
| TypeScript | Type-safe frontend development |
| Vite | Development server and production builds |
| Tailwind CSS v4 | Styling and responsive design |
| Axios | Backend API communication |
| Leaflet | Interactive maps |
| React Leaflet | React integration for Leaflet |
| Lucide React | Interface icons |
| ESLint | Code quality |

## Project Structure

```text
frontend/
├── public/
├── src/
│   ├── api/
│   │   └── axiosInstance.ts
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   └── DashboardLayout.tsx
│   │   ├── routing/
│   │   │   ├── RoutePlanner.tsx
│   │   │   └── RouteResults.tsx
│   │   ├── map/
│   │   │   └── RouteMap.tsx
│   │   └── weather/
│   │       └── WeatherHeatmap.tsx
│   ├── hooks/
│   │   └── useRouteAnalysis.ts
│   ├── pages/
│   │   └── Dashboard.tsx
│   ├── services/
│   │   ├── route.service.ts
│   │   └── heatmap.service.ts
│   ├── types/
│   │   ├── routing.ts
│   │   └── heatmap.ts
│   ├── utils/
│   │   └── apiError.ts
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
├── .env.example
├── package.json
├── vite.config.ts
└── README.md
```

## Getting Started

### Prerequisites

- Node.js and npm
- Running Django backend
- Backend configured with the required OpenRouteService API credentials

### 1. Install dependencies

Open a terminal in the `frontend` directory:

```powershell
npm install
```

### 2. Configure environment variables

Create a `.env` file inside `frontend/`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

The frontend uses this variable to communicate with the Django REST API.

**Note:** Variables prefixed with `VITE_` are exposed to the browser. Never store secret API keys in frontend environment variables.

### 3. Start the development server

```powershell
npm run dev
```

Open the local URL displayed by Vite, typically:

`http://localhost:5173/`

If port 5173 is already in use, Vite may select another available port, such as 5174.

### 4. Build for production

```powershell
npm run build
```

This command runs TypeScript compilation and creates an optimized production build in the `dist/` directory.

### 5. Preview the production build

```powershell
npm run preview
```

## Backend Integration

The frontend communicates with the Django backend using Axios.

The Axios instance is configured in:

`src/api/axiosInstance.ts`

### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/routes/analyze/` | Analyze truck route alternatives |
| POST | `/api/routes/heatmap/` | Retrieve hourly weather-risk data |

### Route Analysis Request

```json
{
  "origin": "Chicago, IL",
  "destination": "Indianapolis, IN",
  "departure_time": "2026-10-16T08:00:00-05:00",
  "load_weight": 20000,
  "checkpoint_interval": 25
}
```

The backend returns route alternatives and their associated weather-risk information.

The frontend displays the results in the route-comparison panel and interactive map.

### Weather Heatmap

After a route is selected, the frontend requests hourly weather-risk data for its checkpoints.

The heatmap presents a 48-hour forecast window, including 49 hourly positions from hour 0 through hour 48.

Users can inspect individual cells to view detailed weather conditions.

The interface also indicates estimated truck arrival times along the route, helping users compare expected travel timing with forecast risk.

## Frontend Architecture

The frontend separates responsibilities into reusable modules.

| Directory | Responsibility |
|---|---|
| `api/` | Axios configuration |
| `components/` | Reusable interface components |
| `hooks/` | Route-analysis state and request handling |
| `pages/` | Dashboard composition |
| `services/` | Backend API requests |
| `types/` | TypeScript data models |
| `utils/` | Shared utility functions |

The dashboard coordinates route selection so the map, comparison panel, and heatmap display information for the selected route.

## Error Handling

The frontend handles common request and validation failures, including:

- Missing required form fields
- Invalid load-weight values
- Invalid origin or destination locations
- Backend request failures
- Weather-data retrieval failures

Backend validation messages are displayed to help users correct their inputs.

For example, an invalid location may return:

```json
{
  "detail": "Location not found: xyznotarealcity123"
}
```

## Code Quality

Run ESLint:

```powershell
npm run lint
```

Run TypeScript compilation and production build:

```powershell
npm run build
```

### Latest Verification Results

- ESLint passed without errors.
- TypeScript compilation passed.
- Vite production build completed successfully.
- 2,025 modules were transformed during the production build.

## Limitations

- The application requires a running backend and internet access to external routing and weather services.
- Weather forecasts may be unavailable for some checkpoints or forecast periods.
- Estimated arrival times do not account for all real-world delays, stops, or changing road conditions.
- The heatmap uses a maximum of 20 sampled route locations.
- A recommended route may still contain hazardous weather conditions.
- The application is a planning aid and should not replace official road advisories or professional dispatch judgment.

## Project Status

The frontend MVP is implemented and integrated with the Django backend.

Route planning, alternative-route comparison, interactive maps, weather-risk visualization, and the 48-hour heatmap have been exercised through the browser.

The latest frontend ESLint and production-build checks completed successfully.