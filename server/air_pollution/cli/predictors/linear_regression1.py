import sys
import json
import io
import pickle
sys.path.append("../../../")
sys.path.append("../../")
from pprint import pprint
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from air_pollution.cli.preprocess.preprocessor import Preprocessor
from air_pollution.common.metric_evaluators import MeanAbsolutePercentageErrorEvaluator
from helper_predictors import *
from pandas import DataFrame
from air_pollution.cli.preprocess.preprocessor import Preprocessor
from air_pollution.common.entities import AqPrediction, AirQuality
from air_pollution.common.repositories import PredictionRepository
import pandas as pd
from sklearn.externals import joblib
import datetime


class LinearRegression(object):
    def __init__(self, city, fit_intercept=True, normalize=True):
        """
        :param fit_intercept: boolean, whether to calculate the intercept for this model.
        no intercept will be used in calculations (e.g. data is expected to be already centered).
        """
        self.city = city
        self.prediction_type = 'linear_regression'
        self.pred_rep = PredictionRepository()
        self.y_predicted = []
        self.regression_object = linear_model.LinearRegression(normalize=normalize, fit_intercept=fit_intercept)
        self.mse_dev = 0.0
        self.variance_score_dev = 0.0
        self.coeffcients = []

    def train_model(self, X_train, y_train):
        """
        trains the linear regression model.
        :param X_train: feature array of training data.
        :param y_train: target array of training data
        """
        self.regression_object.fit(X_train, y_train)


    def predict_and_evaluate(self, X, y, station_id, timestamps=None):
        """
        Makes predictions and evaluates then with mean squared error and variance score.
        :param X: feature array of test or dev data
        :param y: target array of test or dev data
        :param station for which the prediction should be made
        :param timestamps: if None, prediction will not be saved to MongoDB.
        timestamps: 1-column-vector or dataFrame containing all timestamps of y_test
        """
        self.y_predicted = self.regression_object.predict(X)
        if timestamps is not None:
            prediction_frame = self.assign_col_names_and_reindex_with_timestamps(timestamps)
            for day, values in prediction_frame.groupby('timestamp'):
                self.save_predictions_to_mongo_db(station_id, day, values)
        else:
            self.mse = mean_squared_error(y, self.y_predicted)
            self.variance_score = r2_score(y, self.y_predicted)
            self.coeffcients = self.regression_object.coef_



    def assign_col_names_and_reindex_with_timestamps(self, timestamps):
        """
        Reshapes prediction s.t. in every hour is represented in a row again.
        Reassigns column names for predictions and timestamps, s.t. the predictions can be saved to MongoDB
        :param timestamps: timestamps as a timeseries (column of original y_whole_frame)
        :return: prediction_frame: dataFrame with timestamp and column_names for predictions.
        """
        day_count, feat_count = self.y_predicted.shape
        reshaped_predictions = np.reshape(self.y_predicted, (int(day_count*24), feat_count//24))
        if self.city == 'Beijing':
            prediction_frame = DataFrame(reshaped_predictions, columns=['O3', 'PM10', 'PM2.5', 'O3_N' , 'PM10_N', 'PM2.5_N'])
        else:
            prediction_frame = DataFrame(reshaped_predictions, columns=['PM10', 'PM2.5', 'PM10_N', 'PM2.5_N'])

        if prediction_frame.shape[0] == timestamps.shape[0]:
            prediction_frame.loc[:, 'timestamp'] = timestamps.values
        else:
            raise Exception("timestamps and prediction frame must have same shape.")
        return prediction_frame



    def save_predictions_to_mongo_db(self, station, day, predictions):
        """
        Saves predictions of a day for station to MongoDB.
        :param station: str, station for which the prediction where made
        :param day: str, timestamp for which the prediction where made
        :param predictions: dataFrame containing 24 predictions
        """
        current_datetime = np.datetime64(str(day) + ' 23:00:00') - np.timedelta64(1, 'D') # first prediced day: initializes one day before at 23:00
        current_datetime_n = np.datetime64(str(day) + ' 23:00:00')  # 2nd predicted day: initializes one day before at 23:00
        for row in predictions.iterrows():
            row = row[1]
            current_datetime = current_datetime + np.timedelta64(1, 'h')
            pm25 = row['PM2.5']
            pm10 = row['PM10']
            o3 = row['O3'] if 'O3' in row else ''
            aq_entity = vars(AirQuality(pm25=pm25, pm10=pm10, o3=o3, no2='', co='', so2=''))
            aq_pred_day = AqPrediction(station_name=station, utc_time=pd.to_datetime(current_datetime),
                                       prediction_type=self.prediction_type, air_quality=aq_entity, is_first_day=True)
            self.pred_rep.create_prediction(aq_pred_day)

            current_datetime_n = current_datetime_n + np.timedelta64(1, 'h')
            pm25 = row['PM2.5_N']
            pm10 = row['PM10_N']
            o3 = row['O3_N'] if 'O3_N' in row else ''
            aq_entity = vars(AirQuality(pm25=pm25, pm10=pm10, o3=o3, no2='', co='', so2=''))
            aq_pred_day_n = AqPrediction(station_name=station, utc_time=pd.to_datetime(current_datetime_n),
                                       prediction_type=self.prediction_type, air_quality=aq_entity, is_first_day=False)
            self.pred_rep.create_prediction(aq_pred_day_n)


    def save_predictor(self, predictors, city):
        """
        Saves predictor to file
        :param predictor: array of estimators to be saved
        :param city: Beijing or London
        """
        predictors = predictors.flatten()
        path = os.path.join(self.current_dir, '..', '..', 'resources', 'predictors',
                            city + "_" + self.prediction_type + ".pkl")
        with open(path, "wb") as f:
            for model in predictors:
                joblib.dump(model, f)


    def load_predictor(self, city):
        """
        Saves predictor to file
        :param predictor: Estimator to be saved
        :return: array with loaded models
        """
        models = []
        path = os.path.join(self.current_dir, '..', '..', 'resources', 'predictors',
                            city + "_" + self.prediction_type + ".pkl")
        with open(path, "rb") as f:
            while True:
                try:
                    models.append(joblib.load(f))
                except EOFError:
                    break
        return models




def train_model_and_eval_on_naive_split(city, days=365):
    """
    Trains model for each city on naive split
    :param city:
    :param days:
    :return:
    """
    prep = Preprocessor(city, days, predict_days_in_rows=False)
    #prep.preprocess()
    station_ids = prep.read_data_stations(city)[0].pop('station_id').unique()

    for station_id in station_ids:
        X_train_frame, y_train_frame = prep.get_data("train", stationID=station_id, as_vector=False, city=city)
        X_dev_frame, y_dev_frame = prep.get_data("develop", stationID=station_id, as_vector=False, city=city)
        X_test_frame, y_test_frame = prep.get_data("develop", stationID=station_id, as_vector=False, city=city)


        X_train, y_train = prepare_X_and_y(X_train_frame, y_train_frame)
        linear_regression = LinearRegression(city)
        linear_regression.train_model(X_train, y_train)

        # Get whole X and y for prediction on whole dataset for frontend
        # score will there be calculated only on test set).
        X_train_dev = X_train_frame.append(X_dev_frame)
        X_whole_frame = X_train_dev.append(X_test_frame)
        y_train_dev_frame = y_train_frame.append(y_dev_frame)
        y_whole_frame = y_train_dev_frame.append(y_test_frame)
        timestamps_y_whole = y_whole_frame.pop('timestamp')


        # prepare whole data and predict on it, for saving timestamps_y_whole necessary.
        X_whole, y_whole = prepare_X_and_y(X_whole_frame, y_whole_frame)
        linear_regression.predict_and_evaluate(X_whole, y_whole, station_id, timestamps_y_whole)



def crossvalidate_one_model_for_each_station(city, days=365):
    """
    Trains one model for each station and evaluates it by using crossvalidation.
    :param city: string Beijing or London
    :param days: number of days used for crossvalidation.
    """
    prep = Preprocessor(city, days, predict_days_in_rows=False)
    data_cross = prep.read_data_cross_validation(city)
    station_names = data_cross['(0)']['X_train']['station_id'].unique()
    for k,v in data_cross.items():
        for station_name in station_names:
            print("\n\"Partition: ", k, "Station :",  station_name, ":\n")
            X_train_fr, y_train_fr, X_test_fr, y_test_fr = get_frames_for_station_of_datapart_2_frame(station_name, v)
            X_train, y_train = prepare_X_and_y(X_train_fr, y_train_fr)
            X_test, y_test = prepare_X_and_y(X_test_fr, y_test_fr)
            linear_regression = LinearRegression(city)
            linear_regression.train_model(X_train, y_train)
            linear_regression.predict_and_evaluate(X_test, y_test, station_name)
            print("mse: ", linear_regression.mse)
            print("####################################################")


if __name__ == '__main__':

    #crossvalidate_one_model_for_each_station('Beijing', 365)
    train_model_and_eval_on_naive_split('Beijing', 365)
    #crossvalidate_one_model_for_each_station('London', 365)
    train_model_and_eval_on_naive_split('London', 365)