"""
***********************************************
* DataSc - cnns_predictor
* created by : AHMED SGHAIER
* created on : 27.05.18 - 13:52
* copyright : all right reserved @LMU 2018
***********************************************
"""
import sys
sys.path.append("../../../")

from air_pollution.cli.preprocess.preprocessor import Preprocessor
from air_pollution.common.entities import AqPrediction, AirQuality
from air_pollution.common.repositories import PredictionRepository
from tqdm import tqdm
from random import randrange


from tensorflow.python.keras import backend as k_backend
from keras.models import Sequential, load_model
from keras.layers import Conv1D, MaxPooling1D, SpatialDropout1D, Dense, Activation, Reshape, BatchNormalization
from keras.optimizers import Adam

import deepdish as dd
from matplotlib import pyplot
import random
from keras.utils import np_utils
import keras as kr
import numpy as np
import pandas as pd
import gc
import os

class CNN:
    def __init__(self, city, ndays=1, preprocess_data=False, predict_days_in_rows= False):
        '''
        Initialise the different parameters for CNN Class
        :param city:
        :param ndays:
        '''
        self.prediction_name = 'cnn'
        self.predRep = PredictionRepository()
        self.city = city
        self.days = ndays
        self.model = None
        self.preprocess_class = None
        self.preprocess_data = preprocess_data

        self.best_score = np.inf
        self.besthistory = None

        #configs
        self.actuel_config = {}
        self.best_config = {}

        # Settings Parameters
        self.time_steps = 24
        self.output_hours = 48

        # Hyperparameters
        #self.n_hidden_layers = 6
        #self.factor_per_layer = 2
        self.dropout_rate = 0.2

        # Learning Parameters
        self.learning_rate = 0.001

        self.current_dir = os.path.dirname(os.path.realpath(__file__))

        self.predict_features_size = 3 if city == 'Beijing' else 2
        self.predict_days_in_rows = predict_days_in_rows

        self.f_training, self.t_training = pd.DataFrame(), pd.DataFrame()
        self.f_test, self.t_test = pd.DataFrame(), pd.DataFrame()
        self.f_develop, self.t_develop = pd.DataFrame(), pd.DataFrame()

    def intialize_data(self):
        '''
        Initialize the datasets, that will be used to train the model
        using the preprocess class
        :return:
        '''
        self.preprocess_class = Preprocessor('Beijing', 100, self.predict_days_in_rows)

        if self.preprocess_data:
            self.preprocess_class.preprocess()

        self.f_training, self.f_develop, self.f_test, self.t_training, self.t_develop, self.t_test = self.preprocess_class.read_data_stations('Beijing')
        self.f_training = self.f_training.groupby('station_id')
        self.t_training = self.t_training.groupby('station_id')
        self.f_develop = self.f_develop.groupby('station_id')
        self.t_develop = self.t_develop.groupby('station_id')
        self.f_test = self.f_test.groupby('station_id')
        self.t_test = self.t_test.groupby('station_id')

    def initialize_random_model(self, nb_input_features, time_steps=24, nb_outputs_features=3):
        '''
        Initialize a Sequential CNN model using random parameters like nb_hidden_cnv_layers, nb_filter and filter_length

        :param nb_input_features: number of input features
        :param time_steps: number of hours (default 24)
        :param nb_outputs_features: number of the output features
        :return:
        '''
        nb_hidden_cnv_layers = randrange(2, 10)
        nb_filters = random.choice([8, 16, 32, 64, 128])
        filter_length = randrange(3, 6)
        self.actuel_config = {'nb_hidden_cnv_layers': nb_hidden_cnv_layers, 'nb_filters': [nb_filters], 'filter_length': [filter_length]}

        self.model = Sequential()
        self.model.add(Conv1D(input_shape=(time_steps, nb_input_features), filters=nb_filters, kernel_size=filter_length, activation='relu', padding='same'))

        for i in range(nb_hidden_cnv_layers):
            # init radom pramas
            nb_filters = random.choice([8, 16, 32, 64, 128])
            filter_length = randrange(3, 6)

            # save random params
            self.actuel_config['nb_filters'].append(nb_filters)
            self.actuel_config['filter_length'].append(filter_length)

            # init hidden conv layer
            self.model.add(Conv1D(filters=nb_filters, kernel_size=filter_length, padding='same', use_bias=False))
            self.model.add(BatchNormalization())
            self.model.add(Activation('relu'))
            self.model.add(SpatialDropout1D(self.dropout_rate))

        self.model.add(Conv1D(filters=nb_outputs_features*2, kernel_size=1, padding='same'))
        self.model.add(Reshape(target_shape=(2*time_steps, nb_outputs_features)))
        self.model.compile(loss='mse', optimizer='adam')
        #print('##########',self.model.summary())
        #print(self.model.to_json())

    def apply_model_for_each_station(self):
        '''
        Apply the CNN model for each station:
            * train the data
            * search the best model using random search method
            * predict air quality for the next 48hours
            * save the model and configs into hdf5 file
            * save the predictions into the DB
        :return:
        '''
        print('Start predictions for stations')
        with tqdm(total=self.f_training.ngroups,
                  position=1, leave=True,
                  desc='Staions Predictions ',
                  unit='Stations') as progress_bar:     # init progressbar
            for station, values in tqdm(self.f_training):
                self.best_score = np.inf
                self.model = None
                progress_bar.set_postfix(station=station)   # set progressbar suffix
                progress_bar.update()       # update progressbar
                progress_bar.refresh()      # refresh progressbar
                train_X, train_y, dev_X, dev_y, test_X, test_y = self.initialize_data_for_station(station, values)
                self.randomly_best_model(station, train_X, train_y, dev_X, dev_y, test_X, test_y)       # search best model randomly
                self.predict(station)   # predict the AQ data
                self.save_best_configs(station)     # save configs
                os.remove('cnn_cached_model.tmp.hdf5')
        print('End predictions for stations')

    def randomly_best_model(self, station, train_X, train_y, dev_X, dev_y, test_X, test_y):
        '''
        Search a best model randomly using random number of hidden convolution layers, random nuber of filters and random window size
        :param station: a given station
        :param train_X: a given x train vector
        :param train_y: a given y train vector
        :param dev_X:   a given x develop vector
        :param dev_y:   a given y develop vector
        :param test_X:  a given x test vector
        :param test_y:  a given y test vector
        :return:
        '''
        random_iterations = randrange(10, 100)  # get a random number of iterations to find a best model
        with tqdm(total=random_iterations,
                  position=2, leave=True,
                  desc=str("Random Iterations for station " + station),
                  unit='Iteration') as progress_bar2:   # initialize a progressbar
            for iteration in range(random_iterations):
                progress_bar2.set_postfix(iteration=iteration+1)
                progress_bar2.update()
                self.initialize_random_model(nb_input_features=train_X.shape[2], time_steps=self.time_steps, nb_outputs_features=train_y.shape[2])
                history = self.apply_cnn(train_X, train_y, dev_X, dev_y, test_X, test_y)
                self.find_best_model(test_X, test_y, history)

        gc.collect()
        self.model = load_model('cnn_cached_model.tmp.hdf5')

    def find_best_model(self, test_X, test_y, history):
        '''
        Compare the current score with the best score
        if the current score  is better than the best score:
            * assign the best score to the current score
            * save the model as the best model
            * save the configs as the best configs
            * delete the model

        :param test_X: a given x test vector
        :param test_y: a given y test vector
        :param history: a given model history
        :return:
        '''
        score = self.model.evaluate(test_X, test_y)
        if score < self.best_score:
            print()
            print('Found better Score: ', score, ' < ', self.best_score)
            self.best_config = self.actuel_config
            self.best_score = score;
            self.besthistory = history
            self.model.save('cnn_cached_model.tmp.hdf5')
            del self.model
        else:
            print()
            print('Score is worse: ', score, ' > ', self.best_score)
            del self.model

    def apply_cnn(self, train_X, train_y, dev_X, dev_y, test_X, test_y):
        '''
        Fit the CNN model
        :param train_X: a given x train vector
        :param train_y: a given y train vector
        :param dev_X:   a given x develop vector
        :param dev_y:   a given y develop vector
        :param test_X:  a given x test vector
        :param test_y:  a given y test vector
        :return:
        '''
        callback = kr.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=30,
                                              verbose=0, mode='auto')

        return self.model.fit(train_X, train_y, validation_data=(test_X, test_y),
                                 epochs=300, batch_size=10,
                                 verbose=0, shuffle=False, callbacks=[callback] )

    def test_model(self, test_X, test_y):
        '''
        test the model getting the score after giving a test dataset
        :param test_X:  a given x test vector
        :param test_y:  a given y test vector
        :return:
        '''
        score = self.model.evaluate(test_X, test_y)
        print('score: ', score)

    def predict(self, station):
        '''
        Predict the data for a given station
        :param station: a given station
        :return:
        '''
        input_prediction_fram = pd.DataFrame()\
            .append(self.f_training.get_group(station))\
            .append(self.f_test.get_group(station))\
            .append(self.f_develop.get_group(station))

        for day, day_values in input_prediction_fram.groupby('timestamp'):
            predict_X, empty_y= self.clean_and_reshape_frames(day_values)
            predictions = self.model.predict(predict_X)
            predictions = predictions.reshape(predictions.shape[1], predictions.shape[2])
            self.save_predictions(station, day, predictions)

    def save_predictions(self, station, day, predictions):
        '''
        Save a prediction into DB
        :param station: a given station
        :param day: a given day
        :param predictions: a given predictions data
        :return:
        '''
        current_datetime = np.datetime64(str(day) + ' 23:00:00')    # initialize the time stamp on the given day at 23:00 in order to get the next first predict hour after adding 1 hour
        target_features_indices = [*self.t_training._selected_obj.columns]
        target_features_indices.remove('station_id')
        target_features_indices.remove('timestamp')
        i = 0;
        for item in predictions:
            current_datetime = current_datetime + np.timedelta64(1, 'h')    # initialize the next predict hour
            pm25 = item[target_features_indices.index('PM2.5')]  # assign the PM25 attribute
            pm10 = item[target_features_indices.index('PM10')] # assign the PM10 attribute
            o3 = item[target_features_indices.index('O3')] if 'O3' in target_features_indices else ''   # assign the O3 attribute
            aq_entity = vars(AirQuality(pm25=pm25, pm10=pm10, o3=o3, no2='', co='', so2=''))
            aq_pred_day = AqPrediction(station_name=station, utc_time=pd.to_datetime(current_datetime),
                                       prediction_type=self.prediction_name, air_quality=aq_entity, is_first_day=(i<=23))
            self.predRep.create_prediction(aq_pred_day)
            i = i + 1

    def save_best_configs(self, station):
        '''
        Save the best configs for a station
        :param station: a given station
        :return:
        '''
        hdf_file_path = os.path.join(self.current_dir, '..', '..', 'resources', 'predictors', 'cnn', 'cnn_best_configs' + '.hdf5')
        os.makedirs(os.path.dirname(hdf_file_path), exist_ok=True)
        self.best_config = dict(self.best_config)
        self.best_config['score'] = self.best_score
        #self.best_config['model'] = self.model
        dd.io.save(path=hdf_file_path, data={station: self.best_config}, compression=None)

    def plot_result(self, station):
        '''
        plot the history of a given station
        :param station: a given station
        :return:
        '''
        pyplot.title(' Station :'+ station)
        pyplot.plot(self.besthistory.history['loss'], label='train')
        pyplot.plot(self.besthistory.history['val_loss'], label='test')
        pyplot.legend()
        pyplot.show()

        pass

    def initialize_data_for_station(self, station, f_training_for_station):
        '''
        Initialize the data sets of a given station
        :param station: a given station
        :param f_training_for_station: a given feature training frame for a given station
        :return:
        '''
        t_training_for_station = self.t_training.get_group(station)
        f_test_for_station = self.f_test.get_group(station)
        t_test_for_station = self.t_test.get_group(station)
        f_dev_for_station = self.f_develop.get_group(station)
        t_dev_for_station = self.t_develop.get_group(station)

        train_X, train_y = self.clean_and_reshape_frames(f_training_for_station, t_training_for_station)
        test_X, test_y = self.clean_and_reshape_frames(f_test_for_station, t_test_for_station)
        dev_X, dev_y = self.clean_and_reshape_frames(f_dev_for_station, t_dev_for_station)

        return train_X, train_y, dev_X, dev_y, test_X, test_y

    def clean_and_reshape_frames(self, f_frame=None, t_frame=None):
        '''
        Remove unnecessary columns from dataframes
        and reshape it in order to get feature and target frames in the following form:
            feature frame => (n_sample, 24, n_feature)
            target frame => (n_sample, 48, n_target_feature)
        :param f_frame: a given feature frame
        :param t_frame: a given target frame
        :return: reshaped feature and target vectors
        '''
        vector_X, vector_y = pd.DataFrame(), pd.DataFrame()

        feature_cols_to_remove = ['latitude_aq', 'latitude_meo', 'longitude_meo', 'longitude_aq', 'station_id', 'timestamp']
        target_cols_to_remove = ['station_id', 'timestamp']

        if f_frame is not None and np.in1d(feature_cols_to_remove, f_frame.columns).all():
            vector_X = self.preprocess_class.remove_unnecessary_columns(f_frame, feature_cols_to_remove).values
            vector_X = vector_X.reshape((vector_X.shape[0] // self.time_steps), self.time_steps, vector_X.shape[1])

        if t_frame is not None and np.in1d(target_cols_to_remove, t_frame.columns).all():
            vector_y = self.preprocess_class.remove_unnecessary_columns(t_frame, target_cols_to_remove).values
            vector_y = vector_y.reshape((vector_y.shape[0]//self.output_hours), self.output_hours, vector_y.shape[1])

        return vector_X, vector_y


if __name__ == '__main__':
    cnns = CNN('Beijing', 100, preprocess_data=False, predict_days_in_rows=True)
    cnns.intialize_data()
    cnns.apply_model_for_each_station()
    cnns = CNN('London', 100, preprocess_data=False, predict_days_in_rows=True)
    cnns.intialize_data()
    cnns.apply_model_for_each_station()
