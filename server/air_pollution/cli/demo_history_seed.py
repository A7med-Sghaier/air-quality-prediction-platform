"""Local demo data seeder for the portfolio Docker environment.

The original KDD/Biendata live API used by ``extract_history`` is no longer a
reliable runtime dependency. This command creates deterministic, clearly named
sample measurements so the local UI can render charts after station metadata has
been imported.
"""

from datetime import datetime, timedelta
from math import cos, sin

from air_pollution.common.mongo_db import MongoDbAdapter


class DemoHistorySeeder(object):
    def __init__(self, days=14):
        self.days = int(days)
        self.mongodb_adapter = MongoDbAdapter.get_instance()
        self.stations_collection = self.mongodb_adapter.get_collection('stations')
        self.predictions_collection = self.mongodb_adapter.get_collection('predictions')

    def seed(self):
        end_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        timestamps = [end_time - timedelta(hours=hour) for hour in range(self.days * 24)]
        timestamps.reverse()

        aq_count = 0
        me_count = 0
        grid_count = 0

        stations = list(self.stations_collection.find({}, {
            '_id': 1,
            'name': 1,
            'city': 1,
            'station_type': 1,
            'is_grid': 1,
            'latitude': 1,
            'longitude': 1,
        }))

        for station in stations:
            station_type = station.get('station_type')
            is_grid = bool(station.get('is_grid'))

            if station_type == 'aq':
                self.stations_collection.update_one(
                    {'_id': station['_id']},
                    {'$set': {'aq_histories': self._build_air_quality_histories(station, timestamps)}}
                )
                aq_count += 1

            if station_type == 'meo':
                target_field = 'me_grid_histories' if is_grid else 'me_histories'
                self.stations_collection.update_one(
                    {'_id': station['_id']},
                    {'$set': {target_field: self._build_weather_histories(station, timestamps)}}
                )
                if is_grid:
                    grid_count += 1
                else:
                    me_count += 1

        self._seed_predictions(timestamps)

        print('Seeded demo histories: {} AQ stations, {} weather stations, {} grid stations'.format(
            aq_count,
            me_count,
            grid_count,
        ))
        print('Seeded demo predictor: demo_mean')

    def _build_air_quality_histories(self, station, timestamps):
        seed = self._station_seed(station)
        histories = []
        for index, timestamp in enumerate(timestamps):
            daily_wave = sin((index % 24) / 24.0 * 6.28318)
            weekly_wave = cos((index % 168) / 168.0 * 6.28318)
            histories.append({
                'utc_time': timestamp,
                'air_quality': {
                    'pm25': round(28 + seed % 13 + daily_wave * 8 + weekly_wave * 3, 2),
                    'pm10': round(55 + seed % 17 + daily_wave * 12 + weekly_wave * 5, 2),
                    'no2': round(34 + seed % 11 + daily_wave * 7, 2),
                    'co': round(0.55 + (seed % 7) * 0.03 + daily_wave * 0.08, 3),
                    'o3': round(42 + seed % 19 - daily_wave * 9, 2),
                    'so2': round(8 + seed % 5 + weekly_wave * 2, 2),
                }
            })
        return histories

    def _build_weather_histories(self, station, timestamps):
        seed = self._station_seed(station)
        histories = []
        for index, timestamp in enumerate(timestamps):
            daily_wave = sin((index % 24) / 24.0 * 6.28318)
            histories.append({
                'utc_time': timestamp,
                'meteo': {
                    'temperature': round(17 + seed % 8 + daily_wave * 6, 2),
                    'pressure': round(1008 + seed % 15 + cos(index / 24.0) * 4, 2),
                    'humidity': round(52 + seed % 20 - daily_wave * 14, 2),
                    'wind_dire': float((seed * 13 + index * 11) % 360),
                    'wind_speed': round(1.8 + seed % 4 + abs(daily_wave) * 2.3, 2),
                    'weather': self._weather_label(index),
                }
            })
        return histories

    def _seed_predictions(self, timestamps):
        self.predictions_collection.delete_many({'prediction_type': 'demo_mean'})

        prediction_docs = []
        aq_stations = self.stations_collection.find({'station_type': 'aq'}, {'name': 1})
        for station in aq_stations:
            seed = self._station_seed(station)
            for index, timestamp in enumerate(timestamps[-48:]):
                daily_wave = sin((index % 24) / 24.0 * 6.28318)
                prediction_docs.append({
                    'station_name': station['name'],
                    'utc_time': timestamp,
                    'prediction_type': 'demo_mean',
                    'is_first_day': True,
                    'config': {'source': 'local demo seed'},
                    'air_quality': {
                        'pm25': round(29 + seed % 13 + daily_wave * 7, 2),
                        'pm10': round(57 + seed % 17 + daily_wave * 10, 2),
                        'no2': round(35 + seed % 11 + daily_wave * 6, 2),
                        'co': round(0.58 + (seed % 7) * 0.03 + daily_wave * 0.07, 3),
                        'o3': round(40 + seed % 19 - daily_wave * 8, 2),
                        'so2': round(9 + seed % 5, 2),
                    }
                })

        if prediction_docs:
            self.predictions_collection.insert_many(prediction_docs)

    @staticmethod
    def _station_seed(station):
        name = station.get('name', '')
        return sum(ord(char) for char in name)

    @staticmethod
    def _weather_label(index):
        labels = ['Clear', 'Cloudy', 'Overcast', 'Light rain']
        return labels[index % len(labels)]
