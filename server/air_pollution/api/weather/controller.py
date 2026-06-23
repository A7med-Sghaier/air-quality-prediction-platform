import falcon
from bson.json_util import dumps
from air_pollution.common.repositories import StationsRepository
from dateutil.parser import parse
from datetime import datetime, timedelta


class StationWeatherController(object):
    stations_repository = None

    def __init__(self):
        self.stations_repository = StationsRepository()

    def on_get(self, req, res, station_id, is_grid):
        """
        @api {get} /api/stations/:station_id/weather-measurements Get air quality information for given station
        @apiVersion 1.0.0
        @apiName GeStationWeatherMeasurements
        @apiGroup Stations

        @apiParam {String} station_id Stations unique ID.

        @apiSuccess {Object[]} weather_measurement List of air quality entries.
        @apiSuccess {Date} weather_measurement.timestamp timestamp measurement.
        @apiSuccess {Number} weather_measurement.humidity  humidity measurement.
        @apiSuccess {Number} weather_measurement.temperature  temperature measurement.
        @apiSuccess {Number} weather_measurement.pressure  pressure measurement.
        @apiSuccess {Number} weather_measurement.wind_dire  wind_dire measurement.
        @apiSuccess {Number} weather_measurement.wind_speed  wind_speed measurement.
        @apiSuccess {String} weather_measurement.weather  weather measurement.
        @apiSuccessExample {json} Success-Response:
            HTTP/1.1 200 OK
            [
                {
                    "timestamp": 2018-06-12 11:00:00,
                    "humidity": 34,
                    "temperature": 20,
                    "pressure": 1000,
                    "wind_dire": 240,
                    "wind_speed": 1,
                    "weather": "Hail"
                }
            ]
        """
        if 'from' in req.params:
            from_date = parse(req.params['from'])
        else:
            from_date = datetime.now() - timedelta(days=3000)

        if 'to' in req.params:
            to_date = parse(req.params['to'])
        else:
            to_date = datetime.now()

        is_grid = True if is_grid == 'true' else False

        weather_data = self.stations_repository.get_weather_history_for_station(station_id=station_id,
                                                                                from_time=from_date, to_time=to_date,
                                                                                is_grid_station=is_grid)
        res.body = dumps(weather_data, ensure_ascii=False)
        res.status = falcon.HTTP_200
