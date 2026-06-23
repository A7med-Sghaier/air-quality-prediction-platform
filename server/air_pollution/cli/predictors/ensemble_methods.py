import sys
import os

sys.path.append("../../../")
from sklearn.ensemble import GradientBoostingRegressor
from air_pollution.cli.preprocess.preprocessor import Preprocessor
from air_pollution.common.entities import AqPrediction, AirQuality
from air_pollution.common.repositories import PredictionRepository
from helper_predictors import *
from sklearn.externals import joblib
from sklearn.tree import DecisionTreeRegressor

from sklearn.ensemble import AdaBoostRegressor, BaggingRegressor,RandomForestRegressor

import datetime
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.multioutput import MultiOutputRegressor



class Boosting():
    def __init__(self):
        self.params = {}
        self.default_params = {}
        self.prediction_type = ''
        self.estimator = None
        self.param_test = {}

    def init_params_per_station(self, X):
        """
        initialize meta parameters for each station model
        :param X: training feature set
        """
        for station_id, vals in X.groupby('station_id'):
            self.params[station_id] = self.default_params
            #since adaboost has a nested structure, we need multiple parameter storages
            if self.prediction_type=='adaboost' or self.prediction_type=='bagging':
                self.decisiontree_params[station_id] = self.default_tree_params

    def default_regressor(self, X, X_test, y, y_test, station_pred, station_id, regr=None):
        """
        Train estimator and predict next 48 hours of one specific type (airpollutant)
        :param X: training feature set
        :param X_test: testing feature set
        :param y: training target set
        :param y_test: testing target frame
        :param station_pred: dataframe to store the predictions in
        :param type: PM2.5, PM10 or O3
        :return: prediction, dataframe with results, regressor and calculated r2 score
        """

        if regr is None:
            if self.prediction_type == 'gradientboost':
                regr = MultiOutputRegressor(GradientBoostingRegressor(**self.params[station_id]))
            elif self.prediction_type == 'adaboost':
                regr = MultiOutputRegressor(AdaBoostRegressor(DecisionTreeRegressor(**self.decisiontree_params[station_id]),**self.params[station_id]))
            elif self.prediction_type=='bagging':
                regr = MultiOutputRegressor(
                    BaggingRegressor(DecisionTreeRegressor(**self.decisiontree_params[station_id]),
                                      **self.params[station_id]))
            elif self.prediction_type == 'regression_forest':
                regr = MultiOutputRegressor(RandomForestRegressor(**self.params[station_id]))
            regr.fit(X, y)

        y_pred = regr.predict(X_test)
        score = r2_score(y_test,y_pred)
        print("r2 %.4f" % score)
        station_pred['PM10_24'] = y_pred[:,0]
        station_pred['PM10_48'] = y_pred[:,1]
        station_pred['PM2.5_24'] = y_pred[:, 2]
        station_pred['PM2.5_48'] = y_pred[:, 3]

        if y_pred.shape[1]>4:
            station_pred['O3_24'] = y_pred[:, 4]
            station_pred['O3_48'] = y_pred[:, 5]

        return y_pred, station_pred, regr, score

    def grid_search_cv(self, X,y, city):
        """
        Grid search best estimator paramters
        :param X: training feature dataframe
        :param y: training target dataframe
        :param city: London oder Beijing
        :return: array of best estimators
        """
        regressors = np.empty([])
        for station, vals in X.groupby('station_id'):
            y_train = y[y['station_id'] == station]
            vals = vals.drop(
                ['station_id', 'timestamp', 'latitude_aq', 'latitude_meo', 'longitude_aq', 'longitude_meo'], axis=1)

            if city == "Beijing":
                y_train = y_train[['PM10', 'PM10_N', 'PM2.5', 'PM2.5_N', 'O3', 'O3_N']].values
            else:
                y_train = y_train[['PM10', 'PM10_N', 'PM2.5', 'PM2.5_N']].values


            if self.prediction_type == 'gradientboost':
                regr = MultiOutputRegressor(GradientBoostingRegressor(**self.params[station]))
            elif self.prediction_type == 'adaboost':
                regr = MultiOutputRegressor(AdaBoostRegressor(DecisionTreeRegressor(**self.decisiontree_params[station]),**self.params[station]))
            elif self.prediction_type == 'bagging':
                regr = MultiOutputRegressor(
                    BaggingRegressor(DecisionTreeRegressor(**self.decisiontree_params[station]),
                                     **self.params[station]))
            elif self.prediction_type == 'regression_forest':
                regr = MultiOutputRegressor(RandomForestRegressor(**self.params[station]))

            gsearch = RandomizedSearchCV(
                estimator=regr,
                param_distributions=self.param_test,  n_iter=100)
            gsearch.fit(vals.values, y_train)

            print(gsearch.best_params_)
            print(gsearch.best_score_)
            for key, value in gsearch.best_params_.items():
                if self.prediction_type == 'adaboost' or self.prediction_type == 'bagging':
                    if 'base_estimator__' not in key:
                        param_key = key.replace('estimator__', '', 1)
                        self.params[station][param_key] = value
                    else:
                        param_key = key.replace('estimator__base_estimator__', '', 1)
                        self.decisiontree_params[station][param_key] = value
                else:
                    param_key = key.replace('estimator__', '',1)
                    self.params[station][param_key] = value

            #increase learning rate/number estimators
            if 'learning_rate' in self.params[station]:
                self.params[station]['learning_rate'] /= 2
            if 'n_estimators' in self.params[station]:
                self.params[station]['n_estimators'] *= 2

            if self.prediction_type == 'gradientboost':
                best_regr = MultiOutputRegressor(GradientBoostingRegressor(**self.params[station]))
                best_regr.fit(vals.values, y_train)
            elif self.prediction_type == 'adaboost':
                best_regr = MultiOutputRegressor(AdaBoostRegressor(DecisionTreeRegressor(**self.decisiontree_params[station]),**self.params[station]))
                best_regr.fit(vals.values, y_train)
            elif self.prediction_type == 'bagging':
                best_regr = MultiOutputRegressor(BaggingRegressor(DecisionTreeRegressor(**self.decisiontree_params[station]),**self.params[station]))
                best_regr.fit(vals.values, y_train)
            elif self.prediction_type == 'regression_forest':
                best_regr = MultiOutputRegressor(RandomForestRegressor(**self.params[station]))
                best_regr.fit(vals.values, y_train)
            regressors = np.append(regressors, best_regr)
        return regressors[1:]

    def predict(self, city, f_training, f_test, t_training, t_test, regr=None):
        """
        Predict next 48 hours of airpollution for a given test set for a city
        :param city: Beijing or London, depending on data
        :param f_training: featureframe for training the model
        :param f_test: featureframe for testing the model
        :param t_training: targetframe for training the model
        :param t_test: targetframe for testing the model
        :param regr: array of trained regressors (one per station), if given the estimators are used to predict the airpollution, no training involved
        :return: Dataframe with results, array with all regressors, array of r2 scores for each city
        """
        result = pd.DataFrame()
        regressors = np.empty([])
        scores = np.array([])
        i = 0
        for station, vals in f_training.groupby('station_id'):
            print("")
            print("##########")
            print(station)
            f_testing = f_test[f_test['station_id'] == station]
            t_train = t_training[t_training['station_id'] == station]
            t_testing = t_test[t_test['station_id'] == station]

            vals = vals.drop(['station_id', 'timestamp','latitude_aq','latitude_meo','longitude_aq','longitude_meo'], axis=1)
            f_testing = f_testing.drop(['station_id', 'timestamp','latitude_aq','latitude_meo','longitude_aq','longitude_meo'], axis=1)

            station_pred = t_testing.set_index(f_testing.index)
            X = vals.values
            X_test = f_testing.values

            # predict
            if city=="Beijing":
                y = t_train[['PM10', 'PM10_N', 'PM2.5', 'PM2.5_N','O3','O3_N']].values
                y_test = t_testing[['PM10', 'PM10_N', 'PM2.5', 'PM2.5_N','O3','O3_N']].values
            else:
                y = t_train[['PM10', 'PM10_N', 'PM2.5', 'PM2.5_N']].values
                y_test = t_testing[['PM10', 'PM10_N', 'PM2.5', 'PM2.5_N']].values


            if regr is not None:
                predictor = regr[i]
            else:
                predictor = None
            y_pred, station_pred, regressor, score = self.default_regressor(X, X_test,y,y_test,station_pred,station,predictor)

            mse = mean_squared_error(y_test, y_pred)
            print("MSE: %.4f" % mse)
            if regr is None:
                regressors = np.append(regressors, regressor)
            scores = np.append(scores, score)
            result = result.append(station_pred)
            i=i+1
        if regr is None:
            return result, regressors[1:], scores
        else:
            return result, regr, scores

    def gradientboost_cross_val(self,city, dict):
        """
        Cross validation
        :param city: Cityname
        :param dict: dictionary with cross validation split
        :return:
        """
        current_score = -10
        result = []
        for iteration, sets in dict.items():
            res, regr, scores = self.predict(city, sets['X_train'],sets['X_test'],sets['y_train'],sets['y_test'])
            if current_score<np.average(scores):
                result = [res, regr, scores]
        return result[0], result[1]

    def save_predictor(self, predictors, city):
        """
        Saves predictor to file
        :param predictor: array of estimators to be saved
        :param city: Beijing or London
        :return: nothing
        """
        predictors = predictors.flatten()
        path = os.path.join(self.current_dir, '..', '..', 'resources', 'predictors', city+"_"+self.prediction_type+".pkl")
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
        path = os.path.join(self.current_dir, '..', '..', 'resources', 'predictors', city+"_"+self.prediction_type+".pkl")
        with open(path, "rb") as f:
            while True:
                try:
                    models.append(joblib.load(f))
                except EOFError:
                    break
        return models

    def save_prediction(self, prediction, city):
        """
        Save predictions to MongoDB
        :param prediction: Dataframe with predictions
        :return: nothing
        """
        predRep = PredictionRepository()

        prediction_by_station = prediction.groupby('station_id')
        for station, value in prediction_by_station:
            prediction_by_date = value.groupby('timestamp')
            for timestamp, data in prediction_by_date:
                for i in range(data.shape[0]):
                    hourly_pred = data.iloc[[i]]
                    current_time = data.index[i].to_pydatetime()
                    n_day = current_time + datetime.timedelta(days=1)
                    nn_day = current_time + datetime.timedelta(days=2)
                    o3_24 = ''
                    o3_48 = ''
                    if city=='Beijing':
                        o3_24 = float(hourly_pred['O3_24'])
                        o3_48 = float(hourly_pred['O3_48'])
                    aq_entity_day_1 = vars(
                        AirQuality(pm25=float(hourly_pred['PM2.5_24']), pm10=float(hourly_pred['PM10_24']), o3=o3_24, no2='', co='', so2=''))
                    aq_entity_day_2 = vars(
                        AirQuality(pm25=float(hourly_pred['PM2.5_48']), pm10=float(hourly_pred['PM10_48']), o3=o3_48, no2='', co='', so2=''))
                    aq_pred_day_1 = AqPrediction(station_name=station, utc_time=n_day, prediction_type=self.prediction_type,
                                                 air_quality=aq_entity_day_1, is_first_day=True)
                    aq_pred_day_2 = AqPrediction(station_name=station, utc_time=nn_day,
                                                 prediction_type=self.prediction_type, air_quality=aq_entity_day_2, is_first_day=False)
                    predRep.create_prediction(aq_pred_day_1)
                    predRep.create_prediction(aq_pred_day_2)

def predict_new(city,type,days=100, tune=False):
    """
    tune, train and predict with new models
    saves predictors and predictions
    :param city: London or Beijing
    """
    prep = Preprocessor(city, days)
    f_training, f_develop, f_test, t_training, t_develop, t_test = prep.read_data_stations(city)
    f_training = f_training.append(f_develop)
    t_training = t_training.append(t_develop)
    if type == 'adaboost':
        boost = AdaBoost()
    elif type =='bagging':
        boost = Bagging()
    elif type == 'regression_forest':
        boost = RegressionForest()
    else:
        boost = GradientBoost()
    boost.init_params_per_station(f_training)
    predictors = None
    if tune:
        predictors = boost.grid_search_cv(f_training, t_training, city)
    f_test = f_training.append(f_test)
    t_test = t_training.append(t_test)
    beijing, pred, scores = boost.predict(city, f_training, f_test, t_training, t_test, predictors)
    boost.save_prediction(beijing,city)
    if predictors is None:
        boost.save_predictor(pred, city)
    else:
        boost.save_predictor(predictors, city)

def predict_from_file(city,type, days=100):
    """
    predict with models loaded from file
    :param city: London or Beijing
    :return: prediction results
    """
    prep = Preprocessor(city, days)
    f_training, f_develop, f_test, t_training, t_develop, t_test = prep.read_data_stations(city)
    f_training = f_training.append(f_develop)
    f_training = f_training.append(f_test)
    t_training = t_training.append(t_develop)
    t_training = t_training.append(t_test)

    if type == 'adaboost':
        boost = AdaBoost()
    elif type =='bagging':
        boost = Bagging()
    elif type == 'regression_forest':
        boost = RegressionForest()
    else:
        boost = GradientBoost()

    boost.init_params_per_station(f_training)
    pred = boost.load_predictor(city)
    result, _, scores = boost.predict(city,f_training,f_test,t_training,t_test,pred)

    return result



class GradientBoost(Boosting):
    def __init__(self):
        super().__init__()
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.prediction_type = 'gradientboost'
        self.params = {}
        self.default_params = {'max_depth': 5,
                       'n_estimators':60,
                       'max_features': 'sqrt',
                       'min_samples_split': 600,
                       'learning_rate': 0.05,
                       'min_samples_leaf': 50,
                       'subsample':0.8,
                       'random_state':10}
        self.param_test = {'estimator__n_estimators':np.arange(20,81,10),
                           'estimator__max_depth':np.arange(2,16,2), 'estimator__min_samples_split':np.arange(0.001,0.01,0.001),
                           'estimator__min_samples_leaf': np.arange(10, 71, 10),
                           'estimator__max_features':np.arange(1, 20, 1),
                           'estimator__subsample': [0.6, 0.7, 0.75, 0.8, 0.85, 0.9]}

class AdaBoost(Boosting):
    def __init__(self):
        super().__init__()
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.prediction_type = 'adaboost'
        self.params = {}
        self.decisiontree_params = {}
        self.default_tree_params = {'max_depth':5}
        self.default_params = {'n_estimators':60,
                               'learning_rate': 0.05,
                               'loss':'square',
                               'random_state':10}
        self.param_test = {'estimator__n_estimators':np.arange(20,81,10),
                           'estimator__base_estimator__max_depth':np.arange(2,16,2), 'estimator__base_estimator__min_samples_split':np.arange(0.001,0.01,0.001),
                           'estimator__base_estimator__max_features':np.arange(1, 20, 1)}

class Bagging(Boosting):
    def __init__(self):
        super().__init__()
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.prediction_type = 'bagging'
        self.params = {}
        self.decisiontree_params = {}
        self.default_tree_params = {'max_depth':5}
        self.default_params = {'n_estimators':60,
                               'random_state':10}
        self.param_test = {'estimator__n_estimators':np.arange(20,81,10),
                           'estimator__base_estimator__max_depth':np.arange(2,16,2), 'estimator__base_estimator__min_samples_split':np.arange(0.01,0.1,0.01),
                           'estimator__base_estimator__min_samples_leaf': np.arange(0.01,0.1,0.01),
                           'estimator__base_estimator__max_features':np.arange(1, 20, 1),
                           'estimator__max_samples': [0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]}

class RegressionForest(Boosting):
    def __init__(self):
        super().__init__()
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.prediction_type = 'regression_forest'
        self.params = {}
        self.default_params = {'max_depth': 5,
                       'n_estimators':60,
                       'max_features': 'sqrt',
                       'min_samples_split': 600,
                       'min_samples_leaf': 50,
                       'random_state':10}
        self.param_test = {'estimator__n_estimators':np.arange(20,81,10),
                           'estimator__max_depth':np.arange(2,16,2), 'estimator__min_samples_split':np.arange(200,1001,200),
                           'estimator__min_samples_split': np.arange(100, 1000, 100), 'estimator__min_samples_leaf': np.arange(10, 71, 10),
                           'estimator__max_features':np.arange(1, 20, 1)}


if __name__ == '__main__':
    #predict_new('London','gradientboost',tune=True)
    #predict_new('London', 'adaboost', tune=True)
    predict_new('London', 'bagging', tune=True)
    predict_new('London', 'regression_forest', tune=True)

    predict_new('Beijing','gradientboost',tune=True)
    predict_new('Beijing', 'adaboost', tune=True)
    predict_new('Beijing', 'bagging', tune=True)
    predict_new('Beijing', 'regression_forest', tune=True)
    #predict_from_file('London','gradientboost')

    print('Done')