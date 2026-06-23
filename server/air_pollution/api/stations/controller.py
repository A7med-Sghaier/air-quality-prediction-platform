"""
***********************************************
* server - stations
* created by : AHMED SGHAIER
* created on : 22.04.18 - 17:54
* copyright : all right reserved @LMU 2018
***********************************************
"""

import falcon
from bson.json_util import dumps
from air_pollution.common.repositories import StationsRepository


class StationsController(object):
    stations_repository = None

    def __init__(self):
        self.stations_repository = StationsRepository()

    def on_get(self, req, res):
        """
        @api {get} /api/stations Get all stations
        @apiVersion 1.0.0
        @apiName GetAllStations
        @apiGroup Stations

        @apiSuccess {Object[]} station List of stations.
        @apiSuccess {Object} station._id mongodb id field.
        @apiSuccess {String} station._id.$oid actual ID.
        @apiSuccess {String} station.name Name of the station (unique).
        @apiSuccess {Number} station.longitude longitude of the station.
        @apiSuccess {Number} station.latitude latitude of the station.
        @apiSuccess {String} station.city City name where the station is located.
        @apiSuccess {String} station.location_type Type of the station.
        @apiSuccess {Boolean} station.is_grid If the station is a grid station or not.
        @apiSuccess {Boolean} station.need_prediction If the station need a prediction or not.

        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK
          [
            {
               "_id":{
                  "$oid":"5af831903346bbfbc3242777"
               },
               "name":"dongsi",
               "longitude":116.417,
               "latitude":0.417,
               "city":"Beijing",
               "location_type":"Urban",
               "is_grid":false,
               "need_prediction":true
            }
          ]
        """
        stations = self.stations_repository.get_all()
        res.body = dumps(stations, ensure_ascii=False)

        res.status = falcon.HTTP_200


class CityStationsController(object):
    def __init__(self):
        self.stations_repository = StationsRepository()

    def on_get(self, req, res, city_name):
        """
        @api {get} /api/cities/:city_name/stations Get all stations for the given city
        @apiVersion 1.0.0
        @apiName GetAllStationsForCity
        @apiGroup Stations

        @apiParam {String} city_name Name of the city from which we want to receive all stations.

        @apiSuccess {Object[]} station List of stations.
        @apiSuccess {Object} station._id mongodb id field.
        @apiSuccess {String} station._id.$oid actual ID.
        @apiSuccess {String} station.name Name of the station (unique).
        @apiSuccess {Number} station.longitude longitude of the station.
        @apiSuccess {Number} station.latitude latitude of the station.
        @apiSuccess {String} station.city City name where the station is located.
        @apiSuccess {String} station.location_type Type of the station.
        @apiSuccess {Boolean} station.is_grid If the station is a grid station or not.
        @apiSuccess {Boolean} station.need_prediction If the station need a prediction or not.

        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK
          [
            {
               "_id":{
                  "$oid":"5af831903346bbfbc3242777"
               },
               "name":"dongsi",
               "longitude":116.417,
               "latitude":0.417,
               "city":"Beijing",
               "location_type":"Urban",
               "is_grid":false,
               "need_prediction":true
            }
          ]
        """
        stations = self.stations_repository.get_for_city(city_name)

        if stations.count() == 0:
            res.status = falcon.HTTP_404
            return

        res.body = dumps(stations)
        res.status = falcon.HTTP_200
