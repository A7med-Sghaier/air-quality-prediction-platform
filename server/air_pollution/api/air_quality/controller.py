import falcon
from bson.json_util import dumps
from air_pollution.common.repositories import StationsRepository
from dateutil.parser import parse
from datetime import datetime, timedelta


class AirQualityController(object):
    stations_repository = None

    def __init__(self):
        self.stations_repository = StationsRepository()

    def on_get(self, req, res, station_id):
        """
        @api {get} /api/stations/:station_id/air-quality Get air quality information for given station
        @apiVersion 1.0.0
        @apiName GeStationAirQuality
        @apiGroup Stations

        @apiParam {String} station_id Stations unique ID.

        @apiSuccess {Object[]} air_quality List of air quality entries.
        @apiSuccess {Number} air_quality.co  CO measurement.
        @apiSuccess {Number} air_quality.no2  NO2 measurement.
        @apiSuccess {Number} air_quality.o3  O3 measurement.
        @apiSuccess {Number} air_quality.pm10  PM10 measurement.
        @apiSuccess {Number} air_quality.pm25  pm25 measurement.
        @apiSuccess {Number} air_quality.so2  SO2 measurement.
        @apiSuccess {Date} air_quality.timestamp timestamp measurement.
        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK
          [
              {
                "pm25": 1.5,
                "pm10": 20,
                "no2": 1000,
                "co": 1000,
                "co3": 1000,
                "so2": 1000,
                "timestamp": "2018-03-31 20:00:00"
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

        history = self.stations_repository.get_air_quality_history_for_station(station_id=station_id,
                                                                               from_time=from_date,
                                                                               to_time=to_date)
        res.body = dumps(history, ensure_ascii=False)

        res.status = falcon.HTTP_200
