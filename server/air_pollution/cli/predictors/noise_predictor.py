"""
***********************************************
* DataSc - noise_predictor
* created by : AHMED SGHAIER
* created on : 11.05.18 - 19:18
* copyright : all right reserved @LMU 2018
***********************************************
"""

from air_pollution.common.repositories import StationsRepository, PredictionRepository
from air_pollution.common.helper import convert_float_to_int, build_air_quality_for_prediction
from air_pollution.common.entities import Station, AqPrediction

from dateutil.parser import parse
import csv
import datetime
import numpy as np
import pandas as pd


class NoisePredictors:
    def __init__(self, output_path):
        self.stationRepository = StationsRepository()
        self.prediction_repository = PredictionRepository()
        self.output_path = open(output_path, 'w')
        self.predict_cols = ["test_id", "PM2.5", "PM10", "O3"]

    def mean_predictor(self):
        stations = list()
        stations = self.get_histories(stations)

        if len(stations) == 0:
            return

        df = self.build_predictors(stations)
        self.save_predictors(df)
        self.create_submit_file(df)
        return

    def get_histories(self, stations):
        data_limit = 50
        offset = 0
        while True:
            data = self.stationRepository.get_air_quality_history_for_city_old(data_limit, offset, 'Beijing', 12)
            if not data:
                break
            stations.append(pd.DataFrame(data))
            offset += data_limit

        return stations

    def save_predictors(self, data_frame):
        if data_frame.empty:
            return

        groups = data_frame.groupby("station_id")
        today_day = datetime.datetime.now().date()
        tomorrow_day = datetime.date.today() + datetime.timedelta(days=1)

        for key, values in groups:
            station = Station(key)
            for index in values.index.values:
                hour = values['hour'][index] % 24
                time = today_day if values['hour'][index] / 24 >= 1 else tomorrow_day
                time = str(time) + ' ' + str(hour) + ':00:00'
                airq = build_air_quality_for_prediction(values, index)
                prediction = AqPrediction(station_name=station.name,
                                          prediction_type=self.prediction_repository.PREDICTOR_TYPE_MEAN,
                                          utc_time=parse(time), air_quality=airq.__dict__)
                self.prediction_repository.create_prediction(prediction)

    def build_predictors(self, stations):
        data_frame_group = pd.concat(stations).groupby(['station_id', 'test_id'], as_index=False).mean()
        data_frame_group.loc[data_frame_group["O3"] < 0, "O3"] = np.NaN
        return data_frame_group

    def create_submit_file(self, data_frame):
        matrix = data_frame.to_string(columns=self.predict_cols, index=False, header=False, na_rep="::")
        csv_data = list(map(lambda line: list(map(convert_float_to_int, line.split())), matrix.split('\n')))
        csv_data.insert(0, self.predict_cols)

        with self.output_path:
            writer = csv.writer(self.output_path)
            writer.writerows(csv_data)

        self.output_path.close()
        return
