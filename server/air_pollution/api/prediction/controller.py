import falcon
from bson.json_util import dumps
from air_pollution.common.repositories import StationsRepository, PredictionRepository
from air_pollution.common.helper import KEYS, fill_up_air_pollution_keys
from dateutil.parser import parse
from datetime import datetime, timedelta


class PredictorsController(object):
    def __init__(self):
        self.prediction_repository = PredictionRepository()

    def on_get(self, req, res):
        predictors = self.prediction_repository.get_all_predictors()
        result = map(lambda x: {'name': x}, predictors)

        res.body = dumps(result, ensure_ascii=False)
        res.status = falcon.HTTP_200


class PredictionController(object):
    def __init__(self):
        self.station_repository = StationsRepository()
        self.prediction_repository = PredictionRepository()

    def on_get(self, req, res, station_id, predictor_name):
        """
            @api {get} /api/stations/:station_id/predictions Get air quality predictions for given station
            @apiVersion 1.0.0
            @apiName GeStationPrediction
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
                    "timestamp": "2018-03-31-20"
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

        station = self.station_repository.get_by_id(station_id=station_id)

        if not station or 'name' not in station:
            res.status = falcon.HTTP_404
            return

        predictions = self.prediction_repository.get_predictions_for_station(station_name=station['name'],
                                                                             from_date=from_date, to_date=to_date,
                                                                             predictor=predictor_name,
                                                                             only_first_day=True)
        predictions = list(predictions)

        for idx, prediction in enumerate(predictions):
            predictions[idx]['air_quality'] = fill_up_air_pollution_keys(KEYS, prediction['air_quality'], None)

        res.body = dumps(predictions, ensure_ascii=False)
        res.status = falcon.HTTP_200
