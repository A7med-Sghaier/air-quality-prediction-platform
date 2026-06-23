import datetime
import os
import gc
import sys

sys.path.append("../../../")
import random
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.python.keras import backend as K
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, BatchNormalization, Activation
from tensorflow.python.keras.regularizers import l1, l1_l2, l2


from air_pollution.cli.preprocess.preprocessor import Preprocessor
from air_pollution.common.entities import AqPrediction, AirQuality
from air_pollution.common.repositories import PredictionRepository

config = tf.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
# config.gpu_options.per_process_gpu_memory_fraction = 0.48
# config.log_device_placement = True  # to log device placement (on which device the operation ran)
# # (nothing gets printed in Jupyter, only if you run it standalone)
sess = tf.Session(config=config)
tf.keras.backend.set_session(sess)  # set this TensorFlow session as the default session for Keras


class FCNN_Keras:
    # TODO: Discuss, why only Beijing with duration between 12th June and 29th May work
    def __init__(self, city='Beijing', training_epochs=200):
        '''
        Creates a fully connected Sequential Keras model.
        :param city: City of Predictions: Beijing or London
        '''

        # Settings Parameters
        self.n_training_days = 50
        self.input_hours = 24
        self.batch_size = 14
        self.prediction_city = city
        self.prediction_type = 'fcnn'
        self.station_name = ''

        # Hyperparameters
        self.n_hidden_units = 400
        self.n_hidden_layers = 6  # At least 3 Hidden Layers, otherwise Dropout would be bad?
        self.factor_per_layer = 2
        self.n_predictions = 48
        self.dropout_seed = 340
        self.dropout_rate = 0.2

        # Learning Parameters
        self.learning_rate = 0.001
        self.training_epochs = training_epochs

        # activation function
        self.act_fct = "relu"

        # Learning Config
        self.loss_fct = 'mean_squared_error'
        self.optimizer = tf.keras.optimizers.Adam(lr=self.learning_rate)

        # training variables
        self.train_X = 0
        self.test_X = 0
        self.dev_X = 0
        self.dev_Y = 0
        self.train_Y = 0
        self.test_Y = 0

        # prediction variables
        self.prediction_date = 0
        self.predict_X = 0

        # model
        self.model = None

        # evaluation history & prediction
        self.prediction = 0
        self.history = 0

        # Saving and Loading
        self.config = {}
        self.best_score = np.inf
        self.current_dir = os.path.dirname(os.path.realpath(__file__))

    def init_model_train_all(self, experiments=False, n_experiments=200, preprocess=False, store=False):
        '''
        Initializes, models and trains all FCNNs for all stations of a city
        :param preprocess: Flag which indicates if you want to reload and preprocess the Data from MongoDB, default: False (Reading from HDF5-File)
        '''
        # Get preprocessed data from MongoDB
        prep = Preprocessor(self.prediction_city, self.n_training_days)

        self.model = Sequential()

        if preprocess:
            prep.preprocess()

        f_training, f_develop, f_test, t_training, t_develop, t_test = prep.read_data_stations(self.prediction_city)
        self.predict_X = f_training.copy()
        self.predict_X = self.predict_X.append(f_develop)
        self.predict_X = self.predict_X.append(f_test)

        f_training = f_training.groupby('station_id')
        t_training = t_training.groupby('station_id')
        f_develop = f_develop.groupby('station_id')
        t_develop = t_develop.groupby('station_id')
        f_test = f_test.groupby('station_id')
        t_test = t_test.groupby('station_id')

        # TODO: Add parameter to select station
        for station, values in f_training:
            print(station)
            # Train_X and Train_Y for specific city
            f_training_for_city = values
            t_training_for_city = t_training.get_group(station)

            f_develop_for_city = f_develop.get_group(station)
            t_develop_for_city = t_develop.get_group(station)

            f_test_for_city = f_test.get_group(station)
            t_test_for_city = t_test.get_group(station)

            train_X = prep.remove_unnecessary_columns(f_training_for_city,
                                                      ['station_id', 'latitude_aq', 'latitude_meo', 'longitude_aq',
                                                       'longitude_meo',
                                                       'timestamp']).values
            train_Y = prep.remove_unnecessary_columns(t_training_for_city, [
                'station_id',
                'timestamp']).values

            dev_X = prep.remove_unnecessary_columns(f_develop_for_city,
                                                      ['station_id', 'latitude_aq', 'latitude_meo', 'longitude_aq',
                                                       'longitude_meo',
                                                       'timestamp']).values
            dev_Y = prep.remove_unnecessary_columns(t_develop_for_city, [
                'station_id',
                'timestamp']).values

            test_X = prep.remove_unnecessary_columns(f_test_for_city,
                                                     ['station_id', 'latitude_aq', 'latitude_meo', 'longitude_aq',
                                                      'longitude_meo',
                                                      'timestamp']).values
            test_Y = prep.remove_unnecessary_columns(t_test_for_city, [
                'station_id',
                'timestamp']).values

            # Reshaping the data to (n-samples, features) with features being (features_per_hour * windowsize)
            train_X = train_X.reshape(-1, train_X.shape[1] * self.input_hours)
            train_Y = train_Y.reshape(-1, train_Y.shape[1] * self.input_hours)
            dev_X = dev_X.reshape(-1, dev_X.shape[1] * self.input_hours)
            dev_Y = dev_Y.reshape(-1, dev_Y.shape[1] * self.input_hours)
            test_X = test_X.reshape(-1, test_X.shape[1] * self.input_hours)
            test_Y = test_Y.reshape(-1, test_Y.shape[1] * self.input_hours)

            input_set = (train_X, train_Y, dev_X, dev_Y, test_X, test_Y)

            if experiments is False:
                print('####################################################################################')
                print('Testing with params:')
                print('n_hidden_layers: ', self.n_hidden_layers)
                print('n_hidden_units: ', self.n_hidden_units)
                print('factor_per_layer', self.factor_per_layer)
                print('dropout: ', self.dropout)
                print('dropout_rate', self.dropout_rate)
                print('####################################################################################')
                self.create_model(input_set, station_name=station, store=store)
            else:
                # Experiments are done with a random search approach
                for n_opt in range(n_experiments):
                    regularizer_list = np.array([None, l1(), l2(), l1_l2()], dtype=object)
                    regularizer = random.choice(regularizer_list)
                    # regularizer = l1_l2()
                    n_hidden_layers = np.random.randint(3, 10)
                    # n_hidden_layers = 10
                    n_hidden_units = np.random.randint(int(train_X.shape[1]/2), int(3/4 * train_X.shape[1]))
                    # n_hidden_units = 3/4 * train_X.shape[1]
                    factor_per_layer = np.random.randint(100, 125) / 100
                    # factor_per_layer = 1.1
                    dropout = bool(np.random.randint(2))
                    dropout_rate = np.random.randint(10, 80) / 100
                    print('####################################################################################')
                    print('Experiment ', n_opt)
                    print('Testing with params:')
                    print('n_hidden_layers: ', n_hidden_layers)
                    print('n_hidden_units: ', n_hidden_units)
                    print('factor_per_layer', factor_per_layer)
                    print('dropout: ', dropout)
                    print('dropout_rate', dropout_rate)
                    print('regularizer', regularizer)
                    print('####################################################################################')

                    self.create_model(input_set,
                                      n_hidden_layers=n_hidden_layers,
                                      n_hidden_units=n_hidden_units,
                                      factor_per_layer=factor_per_layer,
                                      dropout=dropout,
                                      dropout_rate=dropout_rate,
                                      regularizer=regularizer,
                                      station_name=station,
                                      store=store)

            self.predict(custom_station=station, custom_model=self.model, custom_config=self.config)
            if store is True:
                print('Storing model to HDF5-File')
                self.store_model(custom_model=self.model, station_name=station, custom_config=self.config)

            # reset best score
            self.best_score = np.inf

    def init_station_data(self, station_name, preprocess=False):
        '''
        Loads Data as DataFrame from either HDF5-File or MongoDB and saves it into respective instancevariables
        :param station_name: Station name which shall be evaluated.
        :param preprocess: Flag which indicates if you want to reload and preprocess the Data from MongoDB, default: False (Reading from HDF5-File)
        :return: test_X and test_Y
        '''
        # Get preprocessed data from MongoDB
        prep = Preprocessor(self.prediction_city, self.n_training_days)
        self.station_name = station_name

        if preprocess:
            prep.preprocess()

        f_training, f_develop, f_test, t_training, t_develop, t_test = prep.read_data_stations(self.prediction_city)
        # Use whole history to create predictions for visualization
        self.predict_X = f_training.copy()
        self.predict_X = self.predict_X.append(f_develop)
        self.predict_X = self.predict_X.append(f_test)

        # TODO: This should happen in preprocessing
        f_training = prep.remove_unnecessary_columns(f_training, [
            'latitude_aq',
            'latitude_meo',
            'longitude_aq',
            'longitude_meo',
            'timestamp'])
        t_training = prep.remove_unnecessary_columns(t_training, ['timestamp'])
        f_develop = prep.remove_unnecessary_columns(f_develop, [
            'latitude_aq',
            'latitude_meo',
            'longitude_aq',
            'longitude_meo',
            'timestamp'])
        t_develop = prep.remove_unnecessary_columns(t_develop, ['timestamp'])
        f_test = prep.remove_unnecessary_columns(f_test, [
            'latitude_aq',
            'latitude_meo',
            'longitude_aq',
            'longitude_meo',
            'timestamp'])
        t_test = prep.remove_unnecessary_columns(t_test, ['timestamp'])

        f_training = f_training.groupby('station_id')
        t_training = t_training.groupby('station_id')
        f_develop = f_develop.groupby('station_id')
        t_develop = t_develop.groupby('station_id')
        f_test = f_test.groupby('station_id')
        t_test = t_test.groupby('station_id')

        fcnn_train_X = prep.remove_unnecessary_columns(f_training.get_group(station_name), ['station_id']).values
        fcnn_train_Y = prep.remove_unnecessary_columns(t_training.get_group(station_name), ['station_id']).values
        fcnn_dev_X = prep.remove_unnecessary_columns(f_develop.get_group(station_name), ['station_id']).values
        fcnn_dev_Y = prep.remove_unnecessary_columns(t_develop.get_group(station_name), ['station_id']).values
        fcnn_test_X = prep.remove_unnecessary_columns(f_test.get_group(station_name), ['station_id']).values
        fcnn_test_Y = prep.remove_unnecessary_columns(t_test.get_group(station_name), ['station_id']).values

        # Reshaping the data to (n-samples, features) with features being (features_per_hour * windowsize)
        print(fcnn_train_X.shape)
        self.train_X = fcnn_train_X.reshape(-1, fcnn_train_X.shape[1] * self.input_hours)
        self.train_Y = fcnn_train_Y.reshape(-1, fcnn_train_Y.shape[1] * self.input_hours)
        self.dev_X = fcnn_dev_X.reshape(-1, fcnn_dev_X.shape[1] * self.input_hours)
        self.dev_Y = fcnn_dev_Y.reshape(-1, fcnn_dev_Y.shape[1] * self.input_hours)
        self.test_X = fcnn_test_X.reshape(-1, fcnn_test_X.shape[1] * self.input_hours)
        self.test_Y = fcnn_test_Y.reshape(-1, fcnn_test_Y.shape[1] * self.input_hours)
        print(self.train_X.shape)

        return self.test_X, self.test_Y

    def create_model(self, custom_input=None,
                     n_hidden_layers=None,
                     n_hidden_units=None,
                     factor_per_layer=None,
                     act_fct=None,
                     loss_fct=None,
                     optimizer=None,
                     regularizer=None,
                     station_name=None,
                     dropout=True,
                     dropout_rate=None,
                     store=False):
        '''
        Builds a Sequential Model based on Parameters.
        :param custom_input: Custom input to set the input and output dimensions
        :param n_hidden_layers: Specifies the number of hidden layers
        :param n_hidden_units: Specifies the number of hidden units per layer
        :param factor_per_layer: Specifies the factor in which the hidden units increase per layer
        :param act_fct: Specifies activation function for each node, default: ReLU
        :param loss_fct: Specifies loss function for gradient descent, default: MSE
        :param optimizer: Specifies optimizing algorithm, default: ADAM
        :param station_name: Specifies the station of the model
        :param dropout: Flag which indicates usage of dropout layers
        :param dropout_rate: Rate of dropout layers
        :return:
        '''
        # TODO: Add loss and optimizer. We should create a helper class, since we're all using lossfunctions and optimizers from the same pool
        if n_hidden_layers is None:
            n_hidden_layers = self.n_hidden_layers

        if n_hidden_units is None:
            n_hidden_units = self.n_hidden_units

        if factor_per_layer is None:
            factor_per_layer = self.factor_per_layer

        if act_fct is None:
            act_fct = self.act_fct

        if loss_fct is None:
            loss_fct = self.loss_fct

        if optimizer is None:
            optimizer = self.optimizer

        if dropout_rate is None:
            dropout_rate = self.dropout_rate

        if custom_input is not None:
            train_X, train_Y, dev_X, dev_Y, test_X, test_Y = custom_input
        else:
            train_X = self.train_X
            train_Y = self.train_Y
            dev_X = self.dev_X
            dev_Y = self.dev_Y
            test_X = self.test_X
            test_Y = self.test_Y

        if station_name is None:
            station_name = self.station_name

        config = {
            "n_hidden_layers": n_hidden_layers,
            "n_hidden_units": n_hidden_units,
            "factor_per_layer": factor_per_layer,
            "act_fct": act_fct,
            "loss_fct": loss_fct,
            "regularizer": regularizer.__class__.__name__,
            "optimizer": optimizer.__class__.__name__,
            "station": station_name,
            "dropout": dropout,
            "dropout_rate": dropout_rate
        }
        print('Input ###################################')
        # print(train_X.view())
        print(train_X.shape)
        print('Label ###################################')
        # print(train_Y.view())
        print(train_Y.shape)


        model = None
        model = Sequential()

        # Number of hidden nodes should be higher than feature dimensions, except you want to do "feature selection"
        model.add(Dense(int(n_hidden_units/2), use_bias=False, kernel_initializer="glorot_uniform", input_dim=train_X.shape[1]))
        model.add(BatchNormalization())
        model.add(Activation(act_fct))

        for i in range(1, n_hidden_layers):
            factor_of_layer = (i) * factor_per_layer
            model.add(Dense(int(factor_of_layer * n_hidden_units), use_bias=False, kernel_initializer="he_uniform", kernel_regularizer=regularizer))
            model.add(BatchNormalization())
            model.add(Activation(act_fct))
            if dropout is True:
                model.add(Dropout(dropout_rate, seed=self.dropout_seed))

        # adds output layer with inputs of previous layer and output nodes with the shape of the labels
        model.add(Dense(train_Y.shape[1]))

        # configuring learning process
        model.compile(loss=loss_fct, optimizer=optimizer)

        if custom_input is None:
            self.model = model
            self.config = config
        else:
            self.train_model(custom_model=model,
                             custom_input=custom_input,
                             station_name=station_name,
                             custom_config=config,
                             store=store)
        return model

    def train_model(self, epochs=None, batchsize=None, custom_model=None, custom_input=None, station_name=None,
                    custom_config=None, store=False):
        '''
        Trains model. Can accept custom model and input.
        :param epochs: Specifies number of epochs for training
        :param batchsize: Specifies batchsize of training for systems with small memory
        :param custom_model: Custom model which shall be trained.
        :param custom_input: Custom input which shall be used as training and validation data.
        :param station_name: Specifies the station of the model
        :param custom_config: Describes configuration of the custom_model
        '''

        if isinstance(epochs, int):
            self.training_epochs = epochs

        if isinstance(batchsize, int):
            self.batch_size = batchsize

        if custom_model is not None:
            model = custom_model
        else:
            model = self.model

        if custom_input is not None:
            train_X, train_Y, dev_X, dev_Y, test_X, test_Y = custom_input
        else:
            train_X = self.train_X
            train_Y = self.train_Y
            dev_X = self.dev_X
            dev_Y = self.dev_Y
            test_X = self.test_X
            test_Y = self.test_Y

        if custom_config is None:
            custom_config = self.config

        if station_name is not None:
            station = station_name
        else:
            station = self.station_name

        callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=30, verbose=0,
                                                    mode='auto')

        # train the model with early stopping
        model.fit(train_X, train_Y,
                            epochs=self.training_epochs,
                            batch_size=self.batch_size,
                            validation_data=(dev_X, dev_Y),
                            shuffle=False,
                            callbacks=[callback]
                            )

        if custom_model is None:
            self.model = model
            # self.history = history
            # del history
            gc.collect()
        else:
            # TODO: Continue using config to distinguish between models
            # self.plot_loss_history(history, station_name=station)
            # self.history = history
            print('Current best score: ', self.best_score)
            score = self.test_model(test_X, test_Y, custom_model=model)
            # only update if score is better than best previously recorded score
            if score < self.best_score:
                print('Updated best score: ', score)
                print('Score is better')
                self.best_score = score
                model.save('cached_model')
                # del history
                del model
                gc.collect()
                K.clear_session()
                self.model = tf.keras.models.load_model('cached_model')
                self.optimizer = tf.keras.optimizers.Adam(lr=self.learning_rate)
                custom_config["score"] = score
                self.config = custom_config
                # self.predict(custom_station=station, custom_model=model, custom_config=custom_config)
                # if store is True:
                #     print('Storing model to HDF5-File')
                #     self.store_model(custom_model=self.model, station_name=station, custom_config=custom_config)
            else:
                print('Score is worse')
                self.model.save('cached_model')
                # del history
                del model
                gc.collect()
                K.clear_session()
                self.model = tf.keras.models.load_model('cached_model')
                self.optimizer = tf.keras.optimizers.Adam(lr=self.learning_rate)


    def store_model(self, custom_model=None, station_name=None, custom_config=None):
        '''
        Stores a model to an HDF5-file.
        :param custom_model: Model which shall be saved
        :param station_name: Name of the station of the model
        :param custom_config: Additional Information for naming purposes
        :return:
        '''
        if custom_model is not None:
            model = custom_model
        else:
            model = self.model

        if station_name is None:
            station = self.station_name
        else:
            station = station_name

        filename = self.prediction_city + '_' + station

        hdf_file_path = os.path.join(self.current_dir, '..', '..', 'resources', 'models', self.prediction_type,
                                     self.prediction_city, filename + '.hdf5')
        model.save(hdf_file_path)
        print('Stored')

    def restore_model(self, station_name=None, custom_config=None):
        '''
        Restores a previously saved fcnn-model from an HDF5-file.
        :param station_name: Name of the station of the model which shall be restored
        :param custom_config: Additional Information for naming purposes
        :return: Model which was found with the given parameters
        '''
        if station_name is None:
            station = self.station_name
        else:
            station = station_name

        filename = self.prediction_city + '_' + station

        hdf_file_path = os.path.join(self.current_dir, '..', '..', 'resources', 'models', self.prediction_type,
                                     self.prediction_city, filename + '.hdf5')
        model = tf.keras.models.load_model(hdf_file_path)
        print('Restored')

        self.model = model
        return model

    def plot_loss_history(self, custom_history=None, station_name=None):
        '''
        Plots history with loss and validation_loss. Can plot custom history.
        :param custom_history: Custom history which you want to plot. Currently has to contain "loss" and "val_loss" as keys
        :param station_name: Specifies the station of the model
        '''

        if custom_history is None:
            history = self.history
        else:
            history = custom_history

        if station_name is not None:
            station = station_name
        else:
            station = self.station_name

        # summarize history for loss
        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.title('model loss: ' + station)
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.legend(['train', 'validation'], loc='upper left')
        plt.show()

    def predict(self, input_DF=None, custom_station=None, custom_model=None, custom_config=None):
        '''
        Makes prediction based on input
        :param input_DF: Predictions are made based on this DataFrame.
        :param custom_station: Specifies the station of the model
        :param custom_model: Model used for prediction
        :param custom_config: Describes configuration of the custom_model
        :return:
        '''
        if custom_model is not None:
            model = custom_model
        else:
            model = self.model

        if custom_station is not None:
            station = custom_station
        else:
            station = self.station_name

        # predict_DF has to be a dataframe
        if input_DF is None:
            input_DF = self.predict_X

        prep = Preprocessor(self.prediction_city, self.n_training_days)
        predRep = PredictionRepository()

        input_DF_grouped_by_station = input_DF.groupby('station_id')
        input_DF_per_station = input_DF_grouped_by_station.get_group(station)
        input_DF_per_date = input_DF_per_station.groupby('timestamp')
        prediction_type = self.prediction_type

        for timestamp, value in input_DF_per_date:

            tmp_input = prep.remove_unnecessary_columns(value,
                                                        ['station_id', 'latitude_aq', 'latitude_meo', 'longitude_aq',
                                                         'longitude_meo',
                                                         'timestamp']).values
            tmp_input = tmp_input.reshape(1, -1)
            tmp_prediction = model.predict(tmp_input)

            # Should have 24 rows with 4/6 features, one row per hour of N and NN day
            tmp_prediction = tmp_prediction.reshape(24, -1)

            for i in range(tmp_prediction.shape[0]):
                hourly_pred = tmp_prediction[i]
                current_time = value.index[i].to_pydatetime()
                n_day = current_time + datetime.timedelta(days=1)
                nn_day = current_time + datetime.timedelta(days=2)

                # Distinguish between London and Beijing
                if tmp_prediction.shape[1] == 6:
                    n_pm25 = hourly_pred[2]
                    n_pm10 = hourly_pred[1]
                    n_o3 = hourly_pred[0]
                    nn_pm25 = hourly_pred[5]
                    nn_pm10 = hourly_pred[4]
                    nn_o3 = hourly_pred[3]
                else:
                    n_pm25 = hourly_pred[1]
                    n_pm10 = hourly_pred[0]
                    n_o3 = ''
                    nn_pm25 = hourly_pred[3]
                    nn_pm10 = hourly_pred[2]
                    nn_o3 = ''

                aq_entity_day_1 = vars(AirQuality(pm25=n_pm25, pm10=n_pm10, o3=n_o3, no2='', co='', so2=''))
                aq_entity_day_2 = vars(AirQuality(pm25=nn_pm25, pm10=nn_pm10, o3=nn_o3, no2='', co='', so2=''))
                aq_pred_day_1 = AqPrediction(station_name=station, utc_time=n_day, prediction_type=prediction_type,
                                             air_quality=aq_entity_day_1, config=custom_config, is_first_day=True)
                aq_pred_day_2 = AqPrediction(station_name=station, utc_time=nn_day,
                                             prediction_type=prediction_type, air_quality=aq_entity_day_2, config=custom_config, is_first_day=False)
                predRep.create_prediction(aq_pred_day_1)
                predRep.create_prediction(aq_pred_day_2)

        print('Done predicting')

    def test_model(self, custom_test_X, custom_test_Y, custom_model=None):
        '''
        Evaluates model. Can accept custom test sets.
        :param custom_test_X: Featureset of the testset
        :param custom_test_Y: Targetset of the testset
        :param custom_model: Model used for testing
        :return: Returns the loss as score.
        '''
        test_X = custom_test_X
        test_Y = custom_test_Y
        if custom_model is None:
            model = self.model
        else:
            model = custom_model

        # evaluate performance
        score = model.evaluate(test_X, test_Y)
        print('Current test score: ', score)
        return score


if __name__ == '__main__':
    print('starting fcnn for Beijing...')
    fcnn_beijing = FCNN_Keras(city='Beijing', training_epochs=50)
    fcnn_beijing.init_model_train_all(experiments=True, n_experiments=50, preprocess=False, store=False)
    del fcnn_beijing

    print('starting fcnn for London...')
    fcnn_london = FCNN_Keras(city='London', training_epochs=50)
    fcnn_london.init_model_train_all(experiments=True, n_experiments=50, preprocess=False, store=False)

    # # Train, model and test only one station
    # station = 'donggaocun_aq'
    #
    # fcnn_station = FCNN_Keras(city='Beijing', training_epochs=10)
    # fcnn_station.init_station_data(station_name=station, preprocess=False)
    # # fcnn.init_station_data(station_name='KF1', preprocess=False)
    #
    # # get data
    # input_set = (fcnn_station.train_X, fcnn_station.train_Y, fcnn_station.dev_X, fcnn_station.dev_Y, fcnn_station.test_X, fcnn_station.test_Y)
    #
    # # # Execute once without hyperparam tuning
    # # fcnn_station.create_model()
    # # fcnn_station.train_model(store=False)
    #
    # # Experiments for one station are done with a random search approach
    # for n_opt in range(2):
    #     regularizer_list = np.array([None, l1(), l2(), l1_l2()], dtype=object)
    #     regularizer = random.choice(regularizer_list)
    #     n_hidden_layers = np.random.randint(3, 4)
    #     n_hidden_units = np.random.randint(int(fcnn_station.train_X.shape[1]/2), int(1 * fcnn_station.train_X.shape[1]))
    #     factor_per_layer = np.random.randint(10, 15) / 10
    #     dropout = bool(np.random.randint(2))
    #     dropout_rate = np.random.randint(10, 80) / 100
    #     print('####################################################################################')
    #     print('Testing with params:')
    #     print('n_hidden_layers: ', n_hidden_layers)
    #     print('n_hidden_units: ', n_hidden_units)
    #     print('factor_per_layer', factor_per_layer)
    #     print('dropout: ', dropout)
    #     print('dropout_rate', dropout_rate)
    #     print('regularizer', regularizer)
    #     print('####################################################################################')
    #
    #     fcnn_station.create_model(input_set,
    #                               n_hidden_layers=n_hidden_layers,
    #                               n_hidden_units=n_hidden_units,
    #                               factor_per_layer=factor_per_layer,
    #                               dropout=dropout,
    #                               dropout_rate=dropout_rate,
    #                               regularizer=regularizer,
    #                               station_name=station,
    #                               store=True)
    #
    # # fcnn.restore_model(station_name='donggaocun_aq')
    # fcnn_station.plot_loss_history()
    # print('evaluating...')
    # print('Test-Score')
    # score = fcnn_station.test_model(fcnn_station.test_X, fcnn_station.test_Y)
    # print('Training-Score')
    # pseudo_score = fcnn_station.test_model(fcnn_station.train_X, fcnn_station.train_Y)
    #
    # print('predicting...')
    # fcnn_station.predict()
