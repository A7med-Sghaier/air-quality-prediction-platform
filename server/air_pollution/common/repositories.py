from bson.objectid import ObjectId
from air_pollution.common.mongo_db import MongoDbAdapter
from .helper import normalize_air_quality_for_prediction, normalize_meteo_for_prediction, get_pipline_filter, \
    get_pipline_map
from .helper import extract_air_quality_from_history, extract_weather_data_from_history, \
    parse_air_quality_for_prediction
import itertools
from datetime import datetime, timedelta


class StationsRepository:
    mongodb_adapter = None
    stations_collection = None

    def __init__(self):
        self.mongodb_adapter = MongoDbAdapter.get_instance()
        self.stations_collection = self.mongodb_adapter.get_collection('stations')

    def create_station(self, station):
        """
        create a new station with station values
        :param station: the basic infomation of the new station
        :return new_station: a new station data structure in our program.
        """
        new_station = self.stations_collection.update({"name": station['name']}, {"$set": station}, upsert=True)
        return new_station

    def get_by_id(self, station_id):
        """
        get station structrue by station id
        :param station_id: such as 'dongsi_aq' and so on. it can represent a real station.
        :return : the data structrue of station
        """
        try:
            return self.stations_collection.find_one({'_id': ObjectId(station_id)})
        except:
            return {}

    def add_station_history(self, station, history_label):
        """
        add station structrue to mongodb
        :param station: the data we want to insert into mongodb
        :param history_label: there are three type of history data, aq, me and grid
        :return : 
        """

        attrib_key = 'aq_histories' if history_label == 'aq' else 'me_histories' if history_label == 'me' else 'me_grid_histories'

        new_station = self.stations_collection.update({'name': station['name']},
                                                      {"$addToSet": {attrib_key: {"$each": station[attrib_key]}}})
        if not new_station['updatedExisting']:
            print("ERROR: update failed. you must be sure the cellotion/station exist. the station name is " + str(
                station['name']) + ". update return " + str(new_station['updatedExisting']))
            print("Try: console.py extract_stations")
            # sys.exit()
        return new_station

    def get_all(self):
        """
        get all the data of all station
        """
        return self.stations_collection.find({}, {"aq_histories": 0, "me_histories": 0, "me_grid_histories": 0})

    def get_for_city(self, cityname):
        """
        get data by cityname, maybe 'beijing' or 'london'
        :param cityname: 'beijing' or 'london'
        :return : the whole data of the city
        """
        lowercased = cityname.lower()
        return self.stations_collection.find({'$or': [{'city': cityname}, {'city': lowercased + '_grid'}]},
                                             {'city': 1, 'name': 1, 'longitude': 1, 'latitude': 1, 'location_type': 1,
                                              'station_type': 1, 'is_grid': 1})

    def get_air_quality_history_for_station(self, station_id, from_time, to_time):
        """
        get air quality data the data by station id
        """
        stations = self.stations_collection.aggregate([
            {'$match': {"_id": ObjectId(station_id)}},
            self.create_history_time_extraction_stage(from_time=from_time, to_time=to_time),
            {'$unwind': '$histories'},
            {'$sort': {'histories.utc_time': 1}},
            {'$group': {'_id': '$_id', 'histories': {'$push': '$histories'}}},
        ])

        res = []
        for station in stations:
            for history in station['histories']:
                res.append(extract_air_quality_from_history(history))

        return list(res)

    def get_prediction_for_station(self, station_id):
        """
        get air quality data the data by station id
        """
        stations = self.stations_collection.find(
            {'_id': ObjectId(station_id)},
            {'predictions.air_quality': 1, 'predictions.utc_time': 1}
        ).sort('predictions.utc_time', 1)

        if stations.count() == 0:
            return []

        return list(map(extract_air_quality_from_history, stations[0]['predictions']))

    def get_air_quality_history_for_city_old(self, limit, offset, city, duration):
        """
        !!!deprecated!!!


        :param limit:
        :param offset:
        :param city:
        :param duration:
        :return:
        """
        lastDate = str((datetime.now() - timedelta(days=duration)).date()) + '-0'

        stations = self.stations_collection.find(
            {"$and": [{"city": city}, {"need_prediction": True}]},
            {'name': 1, 'city': 1, 'aq_histories.air_quality': 1, 'aq_histories.utc_time': 1}
        ).skip(offset).limit(limit).sort('aq_histories.utc_time', 1)

        if stations.count() == 0:
            return []

        return list(itertools.chain.from_iterable(map(lambda x: x, map(lambda station: list(
            map(parse_air_quality_for_prediction, range(24), station['aq_histories'],
                [station['name']] * len(station['aq_histories']), [station['city']] * len(station['aq_histories']))),
                                                                       stations))))

    def get_air_quality_history_for_city(self, limit, offset, city, duration):
        """
        get air quality data by some condition
        :param limit: how many data we wanna get
        :param offset: how many data we wanna skip
        :param city: beijing or london
        :param duration: how many days' data we wanna get
        :return: air quality data
        """

        lastDate = str((datetime.now() - timedelta(days=duration)).date())
        pipeline = [
            {
                "$match": {
                    "$and": [
                        {"city": city},
                        {"station_type": "aq"},
                        {"need_prediction": True}
                    ]
                }
            },
            {"$skip": offset},
            {"$limit": limit},
            get_pipline_map("aq_histories", "air_quality"),
            get_pipline_filter(lastDate)
        ]
        stations = list(self.stations_collection.aggregate(pipeline))

        if len(stations) == 0:
            return []

        return list(
            itertools.chain.from_iterable(
                map(lambda x: x,
                    map(lambda station: list(
                        map(normalize_air_quality_for_prediction,
                            station['histories'],
                            [station['name']] * len(station['histories']),
                            [station['city']] * len(station['histories']),
                            [station['latitude']] * len(station['histories']),
                            [station['longitude']] * len(station['histories'])
                            )),
                        stations)
                    )
            )
        )

    def get_meteo_history_for_city(self, limit, offset, city, duration):
        """
        get meteo weather data by some condition
        :param limit: how many data we wanna get
        :param offset: how many data we wanna skip
        :param city: beijing or london
        :param duration: how many days' data we wanna get
        :return: meteo weather data
        """

        lastDate = str((datetime.now() - timedelta(days=duration)).date())
        pipeline = [
            {
                "$match": {
                    "$and": [
                        {"city": city},
                        {"station_type": "meo"},
                    ]
                }
            },
            {"$skip": offset},
            {"$limit": limit},
            get_pipline_map("me_histories", "meteo"),
            get_pipline_filter(lastDate)
        ]

        stations = list(self.stations_collection.aggregate(pipeline))

        if len(stations) == 0:
            return []

        return list(
            itertools.chain.from_iterable(
                map(lambda x: x,
                    map(lambda station: list(
                        map(normalize_meteo_for_prediction,
                            station['histories'],
                            [station['name']] * len(station['histories']),
                            [station['latitude']] * len(station['histories']),
                            [station['longitude']] * len(station['histories'])
                            )),
                        stations)
                    )
            )
        )

    def get_me_grid_history_for_city(self, limit, offset, city, duration):

        """
        get grid weather data by some condition
        :param limit: how many data we wanna get
        :param offset: how many data we wanna skip
        :param city: beijing or london
        :param duration: how many days' data we wanna get
        :return: grid weather data
        """
        lastDate = str((datetime.now() - timedelta(days=duration)).date())
        pipeline = [
            {
                "$match": {
                    "$and": [
                        {"city": city},
                        {"station_type": "meo"}
                    ]
                }
            },
            {"$skip": offset},
            {"$limit": limit},
            get_pipline_map("me_grid_histories", "meteo"),
            get_pipline_filter(lastDate)
        ]

        stations = list(self.stations_collection.aggregate(pipeline))

        if len(stations) == 0:
            return []

        return list(
            itertools.chain.from_iterable(
                map(lambda x: x,
                    list(map(lambda station: list(
                        map(normalize_meteo_for_prediction,
                            station['histories'],
                            [station['name']] * len(station['histories']),
                            [station['latitude']] * len(station['histories']),
                            [station['longitude']] * len(station['histories'])
                            )),
                        stations)
                    ))
            )
        )

    def get_weather_history_for_station(self, station_id, from_time, to_time, is_grid_station=False):
        stations = self.stations_collection.aggregate([
            {'$match': {"_id": ObjectId(station_id)}},
            self.create_history_time_weather_extraction_stage(from_time=from_time, to_time=to_time,
                                                              is_grid_station=is_grid_station),
            {'$unwind': '$histories'},
            {'$sort': {'histories.utc_time': 1}},
            {'$group': {'_id': '$_id', 'histories': {'$push': '$histories'}}},
        ])

        res = []
        for station in stations:
            for history in station['histories']:
                res.append(extract_weather_data_from_history(history))

        return list(res)

    def get_aq_histories_for_station(self, station_name, from_time, to_time):

        """
        get air quality data by station name in a within a specified period of time
        :param station_name: which station's data we wanna get
        :param from_time: we wanna data start from this day
        :param to_time: we wanna data from before this day
        :return: weather data
        """
        stations = self.stations_collection.aggregate([
            {'$match': {"name": station_name}},
            self.create_history_time_extraction_stage(from_time=from_time, to_time=to_time)
        ])

        res = {}
        for station in stations:
            for history in station['histories']:
                # in order to support first and second day predictions we have to
                # also create the proper timestamps for the history
                res[history['utc_time'].isoformat() + '-0'] = history['air_quality']
                res[history['utc_time'].isoformat() + '-1'] = history['air_quality']

        return res

    def create_history_time_weather_extraction_stage(self, from_time, to_time, is_grid_station=False):
        return {
            '$project': {
                "_id": "$_id",
                'name': "$name",
                'city': "$city",
                'histories': {
                    "$filter": {
                        "input": "$me_grid_histories" if is_grid_station else "$me_histories",
                        "as": "history",
                        "cond": {
                            '$and': [
                                {"$gte": ["$$history.utc_time", from_time]},
                                {"$lte": ["$$history.utc_time", to_time]}
                            ]
                        }
                    }
                }
            }
        }

    def create_history_time_extraction_stage(self, from_time, to_time):
        return {
            '$project': {
                "_id": "$_id",
                'name': "$name",
                'city': "$city",
                'histories': {
                    "$filter": {
                        "input": "$aq_histories",
                        "as": "history",
                        "cond": {
                            '$and': [
                                {"$gte": ["$$history.utc_time", from_time]},
                                {"$lte": ["$$history.utc_time", to_time]}
                            ]
                        }
                    }
                }
            }
        }


class PredictionRepository:
    PREDICTOR_TYPE_MEAN = 'mean'
    PREDICTOR_TYPE_FCNN = 'fcnn'

    mongodb_adapter = None
    predictions_collection = None

    def __init__(self):
        self.mongodb_adapter = MongoDbAdapter.get_instance()
        self.predictions_collection = self.mongodb_adapter.get_collection('predictions')

    def get_all_predictors(self):
        return self.predictions_collection.distinct('prediction_type')

    def create_prediction(self, prediction):
        self.predictions_collection.insert_one(prediction.__dict__)

    def get_structured_predictions_for_station(self, predictor, station_name, from_date, to_date):
        predictions = self.get_predictions_for_station(predictor, station_name, from_date, to_date)

        res = {}
        for prediction in predictions:
            postfix = '0' if prediction['is_first_day'] else '1'
            res[prediction['utc_time'].isoformat() + '-' + postfix] = prediction['air_quality']

        return res

    def get_predictions_for_station(self, predictor, station_name, from_date, to_date, only_first_day=False):
        query = {
            'prediction_type': predictor,
            'station_name': station_name,
            'utc_time': {
                '$gt': from_date,
                '$lt': to_date
            }
        }

        if only_first_day:
            query['is_first_day'] = True

        predictions = self.predictions_collection.find(query)

        return predictions
