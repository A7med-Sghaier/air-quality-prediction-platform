# Architecture

Air Quality Prediction Platform is a monorepo that combines a data-visualization frontend, a Python API, MongoDB-backed persistence, and offline data-processing and prediction workflows.

## System Overview

```text
Angular dashboard
  -> Python Falcon API
    -> MongoDB collections
      <- import and preprocessing CLI
      <- trained predictor outputs
```

The application is organized around three main concerns:

- Present air-quality, weather, station, and prediction data in an interactive dashboard.
- Serve normalized data through API endpoints for the frontend.
- Import, preprocess, train, evaluate, and store prediction outputs for later visualization.

## Frontend

The `airPollution/` application is an Angular/TypeScript dashboard. It contains UI components for station maps, station details, weather charts, pollution charts, synchronized charts, and predictor comparison views.

Important frontend areas:

- `src/app/_components/`: dashboard components and page-level views.
- `src/app/_repositories/`: API-facing services that load weather, pollution, prediction, predictor, and metric data.
- `src/app/_models/`: typed frontend models for stations, cities, weather, pollution, charts, predictors, and metrics.
- `src/app/_directives/`: chart-rendering directives for Highcharts and related visualizations.

## Backend API

The `server/air_pollution/api/` package exposes the HTTP API with Falcon. The API is responsible for reading prepared data from MongoDB and shaping it for the frontend.

Main endpoint groups:

- Stations and city station lists.
- Weather measurements per station.
- Air-quality measurements per station.
- Prediction data by station and predictor.
- Predictor and metric summaries.

The API entry point is `server/air_pollution/api/air_app.py`.

## Persistence

MongoDB is used as the application data store. Database access is centralized through the common MongoDB adapter and repository classes in `server/air_pollution/common/`.

The local Docker Compose setup starts MongoDB and passes these values to the API container:

```text
DB_URI=mongodb://mongodb:27017
DB_NAME=air-pollution
```

## Data Pipeline

The CLI code under `server/air_pollution/cli/` handles the offline data workflow:

- Extract historical air-quality and weather data.
- Parse source files into application-ready structures.
- Preprocess and align station, weather, and pollution time-series data.
- Train and run predictor implementations.
- Evaluate predictor quality with metrics such as MAE, MAPE, SMAPE, MSE, and RMSE.
- Store processed data and predictions for API consumption.

## Prediction Layer

Predictor implementations live under `server/air_pollution/cli/predictors/`. The project includes classical ensemble predictors and neural-network based approaches, along with stored model artifacts.

Large trained models and dataset files are intentionally tracked with Git LFS patterns in `.gitattributes`.

## Local Runtime

The project targets legacy runtimes from the original university project period:

- Angular 6 and Node 8 for the frontend.
- Python 3.6 for the backend and ML tooling.
- MongoDB 3.6 for local development.

Docker Compose is the preferred local entry point because it captures those older service assumptions more reliably than a modern host environment.

## Verification Strategy

The current GitHub Actions workflow provides a lightweight portfolio check by compiling the Python source tree:

```bash
python -m compileall -q server/air_pollution
```

This check confirms that the Python modules are syntactically valid without requiring the full historical runtime, data imports, or model dependencies. Frontend verification should be run separately in Docker or a matching Node 8 environment.

## Portfolio Value

This project is useful as a portfolio case study because it demonstrates more than a standalone UI or script. It shows a complete data product shape: visualization, API design, database access, preprocessing, predictive modeling, metrics, Docker-based local services, and CI verification.
