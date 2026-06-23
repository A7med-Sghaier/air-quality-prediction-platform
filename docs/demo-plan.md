# Demo And Screenshot Plan

This document defines the visual material needed before the repository is made public, pinned, or reused in a portfolio profile.

The goal is to show the project as a real full-stack data product without inventing a live demo that has not been verified.

## Demo Goals

The demo material should make these signals obvious within 30 seconds:

- Interactive air-quality and weather dashboard.
- Station map and station-level detail workflow.
- Pollution and weather time-series visualizations.
- Predictor comparison and metric evaluation views.
- Python API and MongoDB-backed data flow.
- Offline preprocessing and prediction pipeline.

## Recommended Screenshots

Capture these screenshots after the application is running locally with safe sample data:

1. Dashboard overview
   - Show the main application shell with city/station context visible.
   - Purpose: gives recruiters an immediate product-level impression.

2. Station map
   - Show air-quality stations on the map.
   - Purpose: demonstrates geospatial UI/API integration.

3. Station details
   - Show station metadata and selected measurements.
   - Purpose: demonstrates drill-down workflow.

4. Pollution chart
   - Show PM2.5, PM10, NO2, O3, SO2, or CO trend visualization.
   - Purpose: demonstrates data visualization and time-series handling.

5. Weather chart
   - Show weather measurements alongside station context.
   - Purpose: demonstrates multi-source data integration.

6. Predictor comparison
   - Show predictor metrics or model comparison charts.
   - Purpose: demonstrates ML evaluation, not just UI work.

7. API response example
   - Show a terminal or API client response from one safe local endpoint.
   - Purpose: demonstrates backend/API ownership.

## README Placement

After screenshots exist, add a short section near the top of the README:

```md
## Demo Preview

![Dashboard overview](docs/images/dashboard-overview.png)
![Station map](docs/images/station-map.png)
![Predictor comparison](docs/images/predictor-comparison.png)
```

Use only screenshots produced from a local, sanitized environment. Do not include private server URLs, real credentials, or non-shareable data.

## Image Storage

Recommended path:

```text
docs/images/
```

Recommended filenames:

```text
dashboard-overview.png
station-map.png
station-details.png
pollution-chart.png
weather-chart.png
predictor-comparison.png
api-response.png
```

Use Git LFS for large image files if they are high resolution or if the folder grows noticeably.

## Demo Verification Checklist

Before adding screenshots to the README:

- Confirm the application runs locally with sanitized configuration.
- Confirm no private hostnames, credentials, or account data are visible.
- Confirm charts and maps are readable at GitHub README size.
- Confirm screenshots support the portfolio positioning sentence.
- Confirm image files are compressed enough for repository browsing.

## Optional Short Demo Video

A short video can be useful later, but it is not required before the first public release. If added, keep it under one minute and show:

1. Opening the dashboard.
2. Selecting a station.
3. Inspecting pollution/weather charts.
4. Viewing predictor comparison metrics.
5. Calling one API endpoint locally.

Store video assets outside the repository unless they are small and intentionally tracked with Git LFS.
