import sys
import os

sys.path.append("../../../")
from air_pollution.common.repositories import StationsRepository
from air_pollution.common.helper_preprocessing import normalize_cyclical_features, haversine, ColumnsLabelEncoder
import string
from sklearn.model_selection import TimeSeriesSplit

import pandas as pd
import numpy as nmp
import matplotlib

matplotlib.use('TkAgg')
from pandas import DataFrame as df
from sklearn import preprocessing
from sklearn.model_selection import KFold
import json
import random


class Preprocessor:
    def __init__(self, city, days, predict_days_in_rows=False):
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.city = city
        self.is_beijing = True if city.lower() == 'beijing' else False
        self.days = days
        self.predic_days_in_rows = predict_days_in_rows
        self.dfs_list = list()
        self.repo = StationsRepository()
        self.dataframes = df()
        self.meteo_station_2_loc = {}
        self.aq_station_2_loc = {}
        self.grid_station_2_loc = {}
        self.aq_2_station = {}
        self.station_2_aq = {}
        self.station_2_train_target = {}
        self.station_2_train_feature = {}
        self.station_2_test_target = {}
        self.station_2_test_feature = {}

    def init_aq_stations_loc_dict(self, dataFrame):
        for station_id, values in dataFrame.groupby('station_id', sort=False):
            self.aq_station_2_loc[station_id] = [values.iloc[0]['latitude'], values.iloc[0]['longitude']]

    def init_meo_stations_loc_dict(self, dataFrame):
        for station_id, values in dataFrame.groupby('station_id', sort=False):
            self.meteo_station_2_loc[station_id] = [values.iloc[0]['latitude'], values.iloc[0]['longitude']]

    def get_data_from_db(self, city, duration_in_days, limit=300):
        """
        Calls functions that extract meteo_frame, grid_frame and aq_frame
        from MongoDB.
        :param city:  string, either London' or 'Beijing'
        :param duration_in_days: int, e.g. 30 -> last 30 days will be inserted
        :param limit: int, max batch size
        :return: dataFrames: meteo_frame, grid_frame, aq_frame
        """
        meteo_frame = self.get_meteo_data(city, duration_in_days, limit)
        grid_frame = self.get_meteo_grid_data(city, duration_in_days, limit)
        aq_frame = self.get_aq_data(city, duration_in_days, limit)

        return meteo_frame, grid_frame, aq_frame

    def get_aq_data(self, city, duration_in_days, limit=300):
        """
       Extracts aq data from MongoDB.
       :param city: either 'London' or 'Beijing'
       :param duration_in_days: int, e.g. 30 -> last 30 days will be inserted
       :param limit: int, max batch size
       :return: dataFrame of aq data
        """
        dataframe = df()
        offset = 0
        while True:
            data = self.repo.get_air_quality_history_for_city(limit, offset, city, duration_in_days)
            if not data:
                break
            dataframe = dataframe.append(df(data))
            offset += limit

        return dataframe

    def get_meteo_data(self, city, duration_in_days, limit=300):
        """
        Extracts meteo data from MongoDB.
        :param city: either 'London' or 'Beijing'
        :param duration_in_days: int, e.g. 30 -> last 30 days will be inserted
        :param limit: int, max batch size
        :return: dataFrame of meteo data
        """
        dataframe = df()
        offset = 0
        while True:
            data = self.repo.get_meteo_history_for_city(limit, offset, city, duration_in_days)
            if not data:
                break
            dataframe = dataframe.append(df(data))
            offset += limit

        return dataframe

    def get_meteo_grid_data(self, city, duration_in_days, limit=300):
        """
        Extracts meteo grid data from MongoDB.
        :param city: either 'London' or 'Beijing'
        :param duration_in_days: e.g. 30 -> last 30 days will be inserted
        :param limit: max batch size
        :return: dataFrame of meteo grid data
        """
        dataframe = df()
        offset = 0
        while True:
            data = self.repo.get_me_grid_history_for_city(limit, offset, str(city+'_grid').lower(), duration_in_days)
            if not data:
                break
            dataframe = dataframe.append(df(data))
            offset += limit

        return dataframe

    def default_preprocess(self, frame, strategy="pchip"):
        self.fill_missing_vals(frame, strategy=strategy)
        return frame

    def get_relation_between_meteo_grid_aq(self):
        """
        The result is unexpected.
            The dongsi_aq, nansanhuan_aq, qianmen_aq, tiantan_aq, wanshouxigong_aq,
            yongdingmennei_aq seem to be too close. After calucation, i find the
            beijing_grid_303 is the closest grid station near all of them.
            And, dongsihuan_aq and nongzhanguan_aq share the same nearest staition, chaoyang_meo.
            And, wanliu_aq and xizhimenbei_aq share the same nearest staition, hadian_meo.

            Store all aq and his nearest grid station or meteo station to file. so we can read them
            from disk.
        """
        for aq_key in self.aq_station_2_loc:
            min_distance_km = 999999.9
            for key in self.meteo_station_2_loc:
                temp_distance = haversine(self.aq_station_2_loc[aq_key], self.meteo_station_2_loc[key])
                if (temp_distance <= min_distance_km):
                    min_distance_km = temp_distance
                    nearest_key = key
            self.station_2_aq[nearest_key] = aq_key
            self.aq_2_station[aq_key] = nearest_key
        f1 = open(os.path.join(self.current_dir, '..', '..', 'resources', 'map_aq2station.json'), 'w')
        f2 = open(os.path.join(self.current_dir, '..', '..', 'resources', 'map_station2aq.json'), 'w')
        f1.write(json.dumps(self.aq_2_station))
        f2.write(json.dumps(self.station_2_aq))
        f1.close()
        f2.close()

    def read_aq_nearest_station_from_disk(self):
        f1 = open(os.path.join(self.current_dir, '..', '..', 'resources', 'map_aq2station.json'), 'r')
        f2 = open(os.path.join(self.current_dir, '..', '..', 'resources', 'map_station2aq.json'), 'r')
        h1 = f1.read()
        h2 = f2.read()
        self.aq_2_station = json.loads(h1)
        self.station_2_aq = json.loads(h2)
        f1.close()
        f2.close()

    def fill_missing_vals(self, frame, strategy, limit_direction):
        """
        Missing values in columns are filled by interpolation.
        :param frame: dataframe
        :param strategy: interpolation strategy, e.g. 'pchip'
        :param limit_direction:
        :return:
        """
        # rame = frame.reindex()
        # If all values of a column are empty set to 0 (interpolation does not work).
        all_null_indexes = frame.isnull().all().compress(lambda x: x == True).index.tolist()

        for key in all_null_indexes:
            frame.fillna({key: 0}, inplace=True)  # drop column of station, when all rows of column empty.
        try:
            frame = frame.interpolate(method=strategy, limit_direction=limit_direction)
        except Exception as e:
            print(e)
            print(limit_direction)

        return frame

    def scale_numeric_feature(self, feature_col):
        """
        Scales given feature to the range of (0, 1).
        :param feature_col: dataframe containing just one feature (= one column).
        :return: dataframe containing scaled feature
        """
        # ToDo: Discuss if this is correct!
        if feature_col.dropna(how="all").empty:
            return feature_col.dropna(how="all")
        scaler = preprocessing.MinMaxScaler()
        scaler.fit(feature_col)
        preprocessing.MinMaxScaler(copy=True, feature_range=(0, 1))
        scaled_feature = scaler.transform(feature_col)
        return scaled_feature

    def transform_weather_to_numeric(self, frame, one_hot=False):
        """
        Transforms weather feature given as string to numeric representation.
        By default each, string gets mapped to a certain number.
        :param  frame: dataframe which contains weather feature
        :param  one_hot: When true, for each string one column is inserted, s.t. the value 0 or 1
        :return: dataframe with weather feature encoded numerically.
        """
        if one_hot:
            frame = pd.get_dummies(frame, prefix='weather', columns=['weather'])
        else:
            ColumnsLabelEncoder(columns=['weather']).fit_transform(frame)
        frame.columns = frame.columns.str.replace('/', '_')

        return frame

    def scale_feature_frame(self, dataframe):
        """
        Scales numeric features, specified in feature_keys set.
        :param dataframe containing all features. Beijing feature frame will should not contain 'O3'.
        :return: dataframe with all numeric features scaled.
        """
        feature_keys = {'CO', 'NO2', 'O3', 'SO2', 'PM2.5', 'PM10', 'longitude_meo', 'longitude_aq', 'latitude_meo',
                        'latitude_aq', 'humidity', 'pressure', 'temperature', 'wind_dire_sin', 'wind_dire_cos',
                        'wind_speed', 'month_sin', 'month_cos', 'hour_sin', 'hour_cos'}
        for key in feature_keys:
            if key in dataframe:
                dataframe[key] = self.scale_numeric_feature(dataframe[key].to_frame())
            else:
                print("Feature", key, "not included in dataframe.")

        return dataframe

    def get_feature_and_target_vector(self, feature_frame, target_frame):
        """
        :param feature_frame:
        :param target_frame:
        :return: feature_vector, target_vector

        """
        feature_group = feature_frame.groupby('station_id', sort=False)
        feature_dict = {}
        for station_id, values in feature_group:
            feature_dict[station_id[:-3]] = values.values

        target_group = target_frame.groupby('station_id', sort=False)
        target_dict = {}
        for station_id, values in target_group:
            target_dict[station_id[:-3]] = values.values
        return feature_dict, target_dict

    def remove_unnecessary_columns(self, df, cols):
        """
        Remove the given columns from DataFrame
        :param df: given DataFrame
        :param cols: given columns to remove
        :return:
        """
        for col in cols:
            df.pop(col)
        return df

    def exclude_all_cols_with_exeptions(self, data_frame, exceptions=[]):
        """
        Remove all columns from a DataFrame except the given columns
        :param data_frame:  given DataFrame
        :param exceptions: given excepts columns to don't be removed
        :return:
        """
        data_frame.reindex()
        cols_to_delete = [x for x in data_frame.columns if x not in exceptions]
        data_frame = data_frame.drop(columns=cols_to_delete)
        return data_frame

    def clean_feature_frame(self, f_frame):
        """
        Feature frame cleaned by transforming weather to numeric, filling missing values,
        normalizing cyclical features (wind_dire, time features) and scaling to range (0, 1).
        :param f_frame: dataFrame, containing features
        :return: f_cleaned: cleaned features
        """
        f_cleaned = pd.DataFrame()
        if f_frame.empty:
            print("Got an empty meteo frame, in clean_meteo_frame")
        else:
            f_numeric = self.transform_weather_to_numeric(f_frame, one_hot=True)
            f_group = f_numeric.groupby('station_id', sort=False)
            for station_id, values in f_group:
                if not values.empty:
                    meteo_interpolated = self.fill_missing_vals(values, strategy="pchip", limit_direction='both')
                    f_normalized = normalize_cyclical_features(meteo_interpolated)
                    f_cleaned = f_cleaned.append(f_normalized)
        return f_cleaned

    def clean_target_frame(self, t_frame):
        """
        Target frame cleaned by filling up missing values with inerpolation.
        No normalization and no scaling necessary as in feature frame!!!
        :param t_frame: dataFrame, containing target values for predictions
        :return: dataFrame, containing only target values for predictions
        """
        t_cleaned = pd.DataFrame()
        if t_frame.empty:
            print("Got an empty aq frame in clean_aq_frame")
        else:

            t_group = t_frame.groupby('station_id', sort=False)
            for station_id, values in t_group:
                t_interpolated = self.fill_missing_vals(values, strategy="linear", limit_direction='both')
                t_cleaned = t_cleaned.append(t_interpolated)
        return t_cleaned

    def dummy_data(self, days=100):
        """
        Generate dummy data for a number f days
        :param days: number of days for which to generate data for, by default 100
        :return: feature and target dataframes
        """
        dummy_features = pd.DataFrame(nmp.random.random((24 * days, 10)), columns=list('ABCDEFGHIJ'))
        dummy_target = pd.DataFrame(nmp.random.randint(200, size=(24 * days, 3)), columns=list('XYZ'))
        return dummy_features, dummy_target

    def get_dummy_data_vectors(self, days=100):
        """
        Get dummy training, develop and test data for x days in numpy array
        :param days: x days for which to get data for, default 100
        :return: feature and target numpy arrays for training, development and testing
        """
        dummy_features, dummy_target = self.dummy_data(days)
        d_features, d_target = self.dummy_data(int(round(days * 0.2)))
        t_features, t_target = self.dummy_data(int(round(days * 0.2)))
        return dummy_features.values, dummy_target.values, d_features.values, d_target.values, t_features.values, t_target.values

    def get_dummy_data_stations_dict(self, stations=10, days=100):
        """
        Get dictionary with dummy data grouped by station
        :param stations: number of stations to get data from
        :param days: number of days to get data for
        :return: dictionary with numpy arrays for training, development and testing grouped by station
        """
        f, t = self.dummy_data(days * stations)
        d_f, d_t = self.dummy_data(int(round(days * stations * 0.2)))
        t_f, t_t = self.dummy_data(int(round(days * stations * 0.2)))

        stations_training = nmp.random.choice(list(string.ascii_letters)[:stations], size=(days * stations * 24))
        stations_develop = nmp.random.choice(list(string.ascii_letters)[:stations],
                                             size=(round(days * stations * 24 * 0.2)))
        stations_test = nmp.random.choice(list(string.ascii_letters)[:stations],
                                          size=(round(days * stations * 24 * 0.2)))

        f['station_id'] = stations_training
        t['station_id'] = stations_training
        d_f['station_id'] = stations_develop
        d_t['station_id'] = stations_develop
        t_f['station_id'] = stations_test
        t_t['station_id'] = stations_test

        f = f.groupby('station_id', sort=False)
        dict = {}
        for station_id, value in f:
            value.pop('station_id')
            t_train = t.loc[t['station_id'] == station_id]
            t_train.pop('station_id')
            t_develop = d_t.loc[d_t['station_id'] == station_id]
            t_develop.pop('station_id')
            f_develop = d_f.loc[d_f['station_id'] == station_id]
            f_develop.pop('station_id')
            t_test = t_t.loc[t_t['station_id'] == station_id]
            t_test.pop('station_id')
            f_test = t_f.loc[t_f['station_id'] == station_id]
            f_test.pop('station_id')
            dict[station_id] = {'train_x': value.values, 'train_y': t_train.values, 'develop_x': f_develop.values,
                                'develop_y': t_develop.values, 'test_x': f_test.values, 'test_y': t_test.values}
        return dict

    def get_f_and_t_for_station(self, station_id, aq_values, meteo_frame):
        """
        For every aq data get the weather data  nearest to it.
        Aq_values for prediction in target_frame
        All other aq values in feature frame.
        :param station_id: station id of air quality station
        :param aq_values: values of air air quality station's aq_group
        :param grid_group:
        :return: feature_frame, target_frame
        """
        meteo_group = meteo_frame.groupby('station_id', sort=False)
        meteo_nearest = self.aq_2_station[station_id]
        meteo_frame = meteo_group.get_group(meteo_nearest)

        meteo_frame = meteo_frame.drop(['station_id'], axis=1)
        feature_frame = meteo_frame.set_index('utc_time').join(aq_values.set_index('utc_time'), lsuffix='_meo',
                                                               rsuffix='_aq')
        feature_frame[['station_id', 'longitude_aq', 'latitude_aq']] = feature_frame[
            ['station_id', 'longitude_aq', 'latitude_aq']].fillna(method='ffill')

        feature_frame, target_frame = self.split_frames_per_days(feature_frame)

        except_cols = ['station_id', 'timestamp', 'PM2.5', 'PM10']
        if self.is_beijing:
            except_cols.extend(['O3', 'PM2.5_N', 'PM10_N', 'O3_N'])
        else:
            except_cols.extend(['PM2.5_N', 'PM10_N'])

        target_frame = self.exclude_all_cols_with_exeptions(target_frame, exceptions=except_cols)
        return feature_frame, target_frame

    def split_frames_per_days(self, data_frame):
        """
        We wanna split the data by day.
        :param data_frame: the dataframe we wanna split
        :return feature_frame, target_frame:
        """
        feature_frame = df()
        target_frame = df()
        target_frame_next = df()

        grouped_per_day_feature_frame = data_frame.groupby('timestamp')
        group_indices = [*grouped_per_day_feature_frame.indices.keys()]

        for day in group_indices[:-2]:
            feature_frame = feature_frame.append(grouped_per_day_feature_frame.get_group(day))

        for next_day in group_indices[1:-1]:
            target_frame = target_frame.append(grouped_per_day_feature_frame.get_group(next_day))

        for next_2nd_day in group_indices[2:]:
            target_frame_next = target_frame_next.append(grouped_per_day_feature_frame.get_group(next_2nd_day))

        target_frame = target_frame.reset_index(drop=True).join(target_frame_next.reset_index(drop=True), rsuffix='_N')

        return feature_frame, target_frame

    def get_feature_and_target_frame(self, meteo_frame, aq_frame):
        """
        Merges aq and meteo data for creating feature and target frame.
        all aqs:   CO', 'NO2', 'O3', 'PM10', 'PM2.5', 'SO2'
        predictions for beijing:  PM2.5/PM10/O3
        predictions for london:   PM2.5/PM10
        Take only stations with aq data and then the meteo data from the next station.
        :param meteo_frame: meteorology dataframe
        :param aq_frame: air quality dataframe
        :return:
          beijing:        meteo_frame + ['CO'] + ['N02'] + ['SO2']
          london:         meteo_frame + ['CO'] + ['N02'] + ['SO2'] + ['O3']
        """
        aq_group = aq_frame.groupby('station_id', sort=False)

        # step two, get feature dataframe.
        #    beijing:        meteo_frame + ['CO'] + ['N02'] + ['SO2']
        #    london:         meteo_frame + ['CO'] + ['N02'] + ['SO2'] + ['O3']

        feature_frame = pd.DataFrame()
        target_frame = pd.DataFrame()
        for station_id, aq_values in aq_group:
            aq_values.pop('timestamp')
            aq_values.pop('hour')
            aq_values.pop('month')
            f_frame_station, t_frame_station = self.get_f_and_t_for_station(station_id, aq_values, meteo_frame)
            feature_frame = feature_frame.append(f_frame_station)
            target_frame = target_frame.append(t_frame_station)
            feature_frame.reindex()
            target_frame.reindex()

        return feature_frame, target_frame

    def remove_unnecessary_grid_stations(self, grid_frame):
        """
        remove the grid stations, which not nearest to aq_stations
        :param grid_frame: grid dataframe
        :return: grid dataframe

        """
        grid_stations = [*grid_frame.groupby('station_id').groups.keys()]
        unnecessary_sations = [x for x in grid_stations if x not in self.station_2_aq.keys()]
        grid_frame = grid_frame.query('station_id not in ["' + ('","').join(map(str, unnecessary_sations)) + '"]')
        grid_frame = grid_frame.reset_index(drop=True)

        return grid_frame

    def fill_missing_row(self, data):
        """
        fill  every station's data which missed in some hours, as a result everyday  has 24 hours
        :param data: dataframe to be filled
        :return: filled dataframe
        """
        if data.empty:
            return data  #

        result = pd.DataFrame()
        data = data.reset_index(drop=True)
        grouped_data = data.groupby(['station_id'])

        for station_id, df_values in grouped_data:
            group_days = df_values.groupby('timestamp')
            print(' fill missing rows for station:', station_id)

            for day, values in group_days:
                new_values = values.reset_index(drop=True)
                hours = values['hour'].values
                for i in range(0, 24):
                    if i not in hours:
                        utc_time = new_values['utc_time'].values[i - 1] + nmp.timedelta64(1, 'h') if i > 0 else nmp.datetime64(str(day) + ' 00:00:00')

                        line = pd.DataFrame({"hour": i, "latitude": new_values['latitude'].values[0],
                                             'longitude': new_values['longitude'].values[0],
                                             "utc_time": utc_time, 'timestamp': values['timestamp'].values[0],
                                             "month": new_values['month'].values[0],
                                             'station_id': new_values['station_id'].values[0]
                                             },
                                            index=[i])

                        new_values = pd.concat([new_values.ix[:i - 1], line, new_values.ix[i:]]).reset_index(drop=True)

                result = result.append(new_values)
        result = result.reset_index(drop=True)
        return result

    def get_split_frames(self, feature_frame, target_frame, split_data_percent=0.8):
        """
        split the data into two parts by split percent
        :param feature_frame: scaled feature frame
        :param target_frame: cleaned target frame
        :param train_data_percent: num
          split size
        :return: two frames  after split
        """
        f_group = feature_frame.groupby(['station_id'])
        t_group = target_frame.groupby(['station_id'])

        f_training_set_frame = df()
        t_training_set_frame = df()
        f_rest_set_frame = df()
        t_rest_set_frame = df()

        train_indices = []
        for station_key, station_feature_values in f_group:

            station_target_data = t_group.get_group(station_key)  # select the target frame for the given station

            group_features_per_day = station_feature_values.groupby('timestamp')  # group the feature frame per days
            group_targets_per_day = station_target_data.groupby('timestamp')  # group the target frame per days

            group_feature_indices = [
                *group_features_per_day.indices.keys()]  # create an array that contains the feature group indexes as dates eg. ['2018-06-20', '2018-06-21', '2018-06-22',...]
            group_target_indices = [
                *group_targets_per_day.indices.keys()]  # create an array that contains the target group indexes as dates eg. ['2018-06-21', '2018-06-22', '2018-06-23',...]

            train_size = int(len(group_feature_indices) * split_data_percent)  # initialize the 80% train length
            if not train_indices:
                train_indices = random.sample(range(len(group_feature_indices)), k=train_size) # get the indexes of days from the previous group_feature_indices array randomly eg. [3, 4, 8, 1, 7,...]

            train_feature_days = nmp.take(group_feature_indices,
                                          train_indices)  # get days from group_feature_indices by the randomly selected indexes eg.['2018-06-22', '2018-06-20', '2018-06-21',...]
            train_target_days = nmp.take(group_target_indices,
                                         train_indices)  # get days from group_target_indices by the randomly selected indexes eg. ['2018-06-23', '2018-06-21', '2018-06-22',...]

            for feature_day in group_feature_indices:
                """
                append the selected feature group by day into the feature training frame
                if the given feature day in train_feature_days array
                otherwise append it into  feature test frame
                """

                if feature_day in train_feature_days:
                    f_training_set_frame = f_training_set_frame.append(group_features_per_day.get_group(feature_day))
                else:
                    f_rest_set_frame = f_rest_set_frame.append(group_features_per_day.get_group(feature_day))

            for target_day in group_target_indices:
                """
                # append the selected target group by day into the target training frame
                # if the given feature day in train_target_days array
                # otherwise append it into  target test frame
                """

                if target_day in train_target_days:
                    t_training_set_frame = t_training_set_frame.append(group_targets_per_day.get_group(target_day))
                else:
                    t_rest_set_frame = t_rest_set_frame.append(group_targets_per_day.get_group(target_day))

        return f_training_set_frame, f_rest_set_frame, t_training_set_frame, t_rest_set_frame

    def get_train_dev_test_frames(self, feature_frame, target_frame, train_data_percent=0.8, dev_data_percent=0.5):
       """
       split data into training set, development set, test set
       training set: 80%
       development set: 10%
       test set: 10%
       at first split 80% as training set, and then split the rest set, half as development set, half as test set.
       :param feature_frame: scaled feature frame
       :param target_frame: cleaned target frame
       :param train_data_percent: num

       :return: training set, development set, test set
       """
       f_train_set, f_rest_set, t_train_set, t_rest_set = self.get_split_frames(feature_frame, target_frame,
           train_data_percent)
       f_dev_set, f_test_set, t_dev_set, t_test_set = self.get_split_frames(f_rest_set, t_rest_set, dev_data_percent)

       return f_train_set, f_dev_set, f_test_set, t_train_set, t_dev_set, t_test_set


    def reshape_next_days_into_rows(self, data_frame):
        """
        reshape the target frame in form 48h for each sample.
        :param data_frame: target data to be reshaped
        :return: reshaped target dataframe
        """
        new_frame = pd.DataFrame()
        cols_to_rows = ['PM2.5_N', 'PM10_N', 'O3_N']
        for station_id, station_values in data_frame.groupby('station_id'):
            groups_per_day = station_values.groupby('timestamp')
            for day, day_values in groups_per_day:
                next_days = list(map(lambda x: str(nmp.datetime64(str(day)) + nmp.timedelta64(1, 'D')), range(24)))
                station = list(map(lambda x: station_id, range(24)))
                new_row = {
                    'station_id': station,
                    'timestamp': next_days,
                    'PM2.5': day_values.pop('PM2.5_N'),
                    'PM10': day_values.pop('PM10_N')
                }

                if 'O3' in day_values:
                    new_row['O3'] = day_values.pop('O3_N')

                day_values = day_values.append(pd.DataFrame(new_row))
                new_frame = new_frame.append(day_values).reset_index(drop=True)

        return new_frame.reset_index(drop=True)

    def save_data(self, filename, f_training, f_develop, f_test, t_training, t_develop, t_test):
        """
        write preprocessed data to hdf5 file for later use
        :param filename: beijing or london
        :param f_training: scaled feature training frame
        :param f_develop: scaled feature development frame
        :param f_test: scaled feature test frame
        :param t_training: cleaned target training frame
        :param t_develop:
        :param t_test: cleaned target test frame
        :return: None
        """
        hdf_file_path = os.path.join(self.current_dir, '..', '..', 'resources', 'preprocess', filename + '.hdf5')
        hdf = pd.HDFStore(hdf_file_path)
        hdf.put('f_training', f_training, format='table', data_columns=True)
        hdf.put('t_training', t_training, format='table', data_columns=True)
        hdf.put('f_develop', f_develop, format='table', data_columns=True)
        hdf.put('t_develop', t_develop, format='table', data_columns=True)
        hdf.put('f_test', f_test, format='table', data_columns=True)
        hdf.put('t_test', t_test, format='table', data_columns=True)
        hdf.close()


    def save_data_cross_validation(self, filename, dict):
        """
        write preprocessed data to hdf5 file for later use
        :param filename: beijing or london
        :return: None
        """
        filename = filename + 'cross_validation'
        hdf_file_path = os.path.join(self.current_dir, '..', '..', 'resources', 'preprocess', filename + '.hdf5')
        hdf = pd.HDFStore(hdf_file_path)
        for key, value in dict.items():
            hdf.put('/(%d)/X_train' % key, value['X_train'].infer_objects(), format='table', data_columns=True)
            hdf.put('/(%d)/X_test' % key, value['X_test'].infer_objects(), format='table', data_columns=True)
            hdf.put('/(%d)/y_train' % key, value['y_train'].infer_objects(), format='table', data_columns=True)
            hdf.put('/(%d)/y_test' % key, value['y_test'].infer_objects(), format='table', data_columns=True)

        hdf.close()


    def read_data_cross_validation(self, filename):
        """
        get training, and test  data for cross validation as a dictionary from hdf5 file
        columns targets: PM2.5, PM10, [O3](Beijing only)
        :param filename: beijing or london
        :return: feature training set, feature test set, target training set, target test set in a dictionary
        """
        filename = filename + 'cross_validation'
        hdf_file_path = os.path.join(self.current_dir, '..', '..', 'resources', 'preprocess', filename + '.hdf5')
        with pd.HDFStore(hdf_file_path) as hdf:
            dict = {}
            for key in list(map(lambda x: x.split('/')[1], hdf.keys())):
                dict[key] = {'X_train': hdf.get(key + '/X_train'), 'X_test': hdf.get(key + '/X_test'),
                             'y_train': hdf.get(key + '/y_train'), 'y_test': hdf.get(key + '/y_test')}
        return dict


    def read_data_stations(self, filename):
        """
        get training, develop, test per station in a dictionary from hdf5 file
        columns targets: PM2.5, PM10, [O3](Beijing only)
        :param filename: beijing or london
        :return: feature training set, feature test set, target training set, target test set in a dictionary
        """
        if self.predic_days_in_rows:
            filename = filename + '_48_in_row'

        hdf_file_path = os.path.join(self.current_dir, '..', '..', 'resources', 'preprocess', filename + '.hdf5')

        f_training = pd.read_hdf(hdf_file_path, key='f_training', mode='r')
        t_training = pd.read_hdf(hdf_file_path, key='t_training', mode='r')
        f_develop = pd.read_hdf(hdf_file_path, key='f_develop', mode='r')
        t_develop = pd.read_hdf(hdf_file_path, key='t_develop', mode='r')
        f_test = pd.read_hdf(hdf_file_path, key='f_test', mode='r')
        t_test = pd.read_hdf(hdf_file_path, key='t_test', mode='r')
        return f_training, f_develop, f_test, t_training, t_develop, t_test


    def split_for_cross_validation(self, X_frame, y_frame, split=3):
        """
        split data for cross validation
        :param X_frame: features in dataframe
        :param y_frame: targets in dataframe
        :param split: number of splits
        :return: dictionary of all splitted feature and target frames
        """
        tscv = TimeSeriesSplit(n_splits=split)
        dict = {}
        i = 0
        # get all days
        group_features_per_day = X_frame.groupby('timestamp')
        group_feature_indices = nmp.array([*group_features_per_day.indices.keys()])

        # split by days
        for train_indices, test_indices in tscv.split(group_feature_indices):
            # assign days from feature and target frame to corresponding frame
            X_train = X_frame[X_frame['timestamp'].isin(group_feature_indices[train_indices])]
            X_test = X_frame[X_frame['timestamp'].isin(group_feature_indices[test_indices])]

            temp_frame = X_frame.reset_index()
            target_indices_train = temp_frame.index[
                X_frame['timestamp'].isin(group_feature_indices[train_indices])].tolist()
            target_indices_test = temp_frame.index[
                X_frame['timestamp'].isin(group_feature_indices[test_indices])].tolist()

            y_train = y_frame.iloc[target_indices_train]
            y_test = y_frame.iloc[target_indices_test]

            dict[i] = {'X_train': X_train, 'X_test': X_test, 'y_train': y_train, 'y_test': y_test}
            i = i + 1
        return dict


    def get_station_data_as_numpy_array(self, data, stationID):
        """
        get data as numpy array from a single station
        :param stationID: str
        station_id
        """
        if stationID is None:
            return nmp.array(data)
        else:
            data_group = data.groupby(["station_id"])
            result_frame = data_group.get_group(stationID)
            return nmp.array(result_frame)


    def get_station_dataframe(self, data, stationID):
        """
        get dataframe from a single station
        :param stationID: str
        station_id
        """
        if stationID is None:
            return data
        else:
            data_group = data.groupby(["station_id"])
            result_frame = data_group.get_group(stationID)
            return result_frame


    def get_station_f_t_numpy_array(self, f_training, f_develop, f_test, t_training, t_develop, t_test, stationID):
        """
         get feature numpy array  or target numpy array from a single station
         :param stationID: str
         station_id
         """
        f_train_array = self.get_station_data_as_numpy_array(f_training, stationID)
        f_test_array = self.get_station_data_as_numpy_array(f_test, stationID)
        f_develop_array = self.get_station_data_as_numpy_array(f_develop, stationID)
        t_develop_array = self.get_station_data_as_numpy_array(t_develop, stationID)
        t_train_array = self.get_station_data_as_numpy_array(t_training, stationID)
        t_test_array = self.get_station_data_as_numpy_array(t_test, stationID)
        return f_train_array, f_develop_array, f_test_array, t_train_array, t_develop_array, t_test_array


    def reshape_numpy_array(self, data_narray, is_feature=True):
        """
         reshape data from a single station in form
            x: (n_samples, 24, n_input_features)
            y: (n_samples, 48, n_output_features)
         :param is_feature: bool
         the to be reshaped data is Feature frame or  Target Frame
         """

        rows_count, columns_count = data_narray.shape

        if self.predic_days_in_rows == True and is_feature == False:
            n_samples = rows_count // 48
            result = nmp.reshape(data_narray, (int(n_samples), 48, data_narray.shape[1]))
        else:
            n_samples = rows_count // 24
            result = nmp.reshape(data_narray, (int(n_samples), 24, data_narray.shape[1]))

        return result


    def get_train_develop_test_array(self, part, f_train_array, f_develop_array, f_test_array, t_train_array,
                                     t_develop_array, t_test_array):
        """
        Get train array or test array
        :param part: str
        The part ( "train" ,"develop" or  "test")
        :param city
        "Beijing"or "London"
        """
        if part == "train":
            f_train_reshape_array = self.reshape_numpy_array(f_train_array, True)
            t_train_reshape_array = self.reshape_numpy_array(t_train_array, False)
            return f_train_reshape_array, t_train_reshape_array
        elif part == "develop":
            f_develop_reshape_array = self.reshape_numpy_array(f_develop_array, True)
            t_develop_reshape_array = self.reshape_numpy_array(t_develop_array, False)
            return f_develop_reshape_array, t_develop_reshape_array

        else:
            f_test_reshape_array = self.reshape_numpy_array(f_test_array, True)
            t_test_reshape_array = self.reshape_numpy_array(t_test_array, False)
            return f_test_reshape_array, t_test_reshape_array

    def preprocess(self):
        """
        preprocess data
        :param city: city to get the data from
        :param days: days from which to get the data from
        :param predict_days_in_rows: weather the target frame in 48_rows format
        :return: feature and target vectors
        """
        meteo_frame, grid_frame, aq_frame = self.get_data_from_db(self.city, self.days)

        # fill missing row, after these function, every day has data of 0~23 hour
        # meteo_frame = self.fill_missing_row(meteo_frame)

        # Initializing dictionaries mapping aq stations to nearest meteo and vice versa.
        self.init_aq_stations_loc_dict(aq_frame)
        self.init_meo_stations_loc_dict(grid_frame)
        self.get_relation_between_meteo_grid_aq()
        self.read_aq_nearest_station_from_disk()

        grid_frame = self.remove_unnecessary_grid_stations(grid_frame)
        grid_frame = self.fill_missing_row(grid_frame)
        aq_frame = self.fill_missing_row(aq_frame)

        # initialize and clean  feature and target frames
        print('* Splitting frames into Features and Target Frame')
        feature_frame, target_frame = self.get_feature_and_target_frame(grid_frame, aq_frame)
        print('* End Split')
        print('* cleaning Feature Frame ...')
        cleaned_feature_frame = self.clean_feature_frame(feature_frame)
        print('* End cleaning Feature Frame!')
        print('* cleaning Target Frame ...')
        cleaned_target_frame = self.clean_target_frame(target_frame)
        print('* End cleaning Target Frame!')

        # scale feature frame
        scaled_f_frame = self.scale_feature_frame(cleaned_feature_frame)

        '''
        ############################################################################################
        #
        # split the data into feature training, feature test, target train and target test
        # than save the splited frames into hdf5 in the 24_rows format 
        #
        ############################################################################################
        '''
        f_train_set, f_dev_set, f_test_set, t_train_set, t_dev_set, t_test_set = self.get_train_dev_test_frames(
            scaled_f_frame, cleaned_target_frame, 0.8, 0.5)
        dict = self.split_for_cross_validation(scaled_f_frame, cleaned_target_frame)
        self.save_data(self.city, f_train_set, f_dev_set, f_test_set, t_train_set, t_dev_set, t_test_set)
        self.save_data_cross_validation(self.city, dict)

        '''
        ############################################################################################
        #
        # reform the target frames from 24_roes into 48_rows format 
        # then save the feature and reformed target frames into 2.nd hdf5 
        #
        ############################################################################################
        '''
        if self.predic_days_in_rows:
            t_train_set_in_rows = self.reshape_next_days_into_rows(t_train_set)
            t_dev_set_in_rows = self.reshape_next_days_into_rows(t_dev_set)
            t_test_set_in_rows = self.reshape_next_days_into_rows(t_test_set)
            self.save_data(self.city + '_48_in_row', f_train_set, f_dev_set, f_test_set, t_train_set_in_rows,
                           t_dev_set_in_rows, t_test_set_in_rows)


    def get_data(self, part, stationID=None, as_vector=True, city="Beijing"):
        """
        Get data for training predictors.

        :param part: str
          The part ( "train" "develop" or "test")
        :param stationID：str
          the name of station, get training data of a single station
        :param as_vector: bool
          Whether to get the reshaped data.
          if False, the training data is Pandas Datafrme.
        :param city: str
          either "Beijing" or "London
        """
        f_training, f_develop, f_test, t_training, t_develop, t_test = self.read_data_stations(city)

        if as_vector:
            f_train_array, f_develop_array, f_test_array, t_train_array, t_develop_array, t_test_array = self.get_station_f_t_numpy_array(
                f_training,
                f_develop,
                f_test,
                t_training,
                t_develop,
                t_test,
                stationID)
            feature_reshap_array, target_reshap_array = self.get_train_develop_test_array(part, f_train_array,
                                                                                          f_develop_array,
                                                                                          f_test_array, t_train_array,
                                                                                          t_develop_array, t_test_array)
            return feature_reshap_array, target_reshap_array
        else:
            if part == "train":
                f_training_frame = self.get_station_dataframe(f_training, stationID)
                t_training_frame = self.get_station_dataframe(t_training, stationID)
                return f_training_frame, t_training_frame
            elif part == "develop":
                f_develop_frame = self.get_station_dataframe(f_develop, stationID)
                t_develop_frame = self.get_station_dataframe(t_develop, stationID)
                return f_develop_frame, t_develop_frame
            else:
                f_test_frame = self.get_station_dataframe(f_test, stationID)
                t_test_frame = self.get_station_dataframe(t_test, stationID)
                return f_test_frame, t_test_frame


if __name__ == '__main__':
    prep = Preprocessor('London', 100, predict_days_in_rows=False)
    prep.preprocess()

    # f_training, f_develop, f_test, t_training, t_develop, t_test = prep.read_data_stations('Beijing')
    # dict = prep.read_data_cross_validation('Beijing')

    # x_train, y_train = prep.get_data(part="develop", as_vector=True, city="Beijing")
    # print(x_train, y_train)
