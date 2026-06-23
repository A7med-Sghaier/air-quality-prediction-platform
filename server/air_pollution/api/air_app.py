"""
***********************************************
* madPandas__ - airApp
* created by : AHMED SGHAIER
* created on : 22.04.18 - 16:58
* copyright : all right reserved @LMU 2018
***********************************************
"""
import falcon
from falcon_cors import CORS

from air_pollution.api.metrics.controller import StationMetricsController, MetricController, MetricsController
from .stations.controller import StationsController, CityStationsController
from .air_quality.controller import AirQualityController
from .weather.controller import StationWeatherController
from .prediction.controller import PredictionController, PredictorsController

cors = CORS(allow_all_origins=True)
pandasApi = falcon.API(middleware=[cors.middleware])

pandasApi.add_route('/api/stations', StationsController())
pandasApi.add_route('/api/stations/{station_id}/weather-measurements/{is_grid}', StationWeatherController())
pandasApi.add_route('/api/stations/{station_id}/air-quality', AirQualityController())
pandasApi.add_route('/api/stations/{station_id}/predictions/{predictor_name}', PredictionController())
pandasApi.add_route('/api/cities/{city_name}/stations', CityStationsController())

pandasApi.add_route('/api/metrics', MetricsController())
pandasApi.add_route('/api/predictors', PredictorsController())
pandasApi.add_route('/api/predictors/{predictor}/metrics/{station_name}', StationMetricsController())
pandasApi.add_route('/api/predictors/{predictor}/metrics/{station_name}/{metric_name}', MetricController())
