import io
import json
import numpy as np
import sys
sys.path.append("../../../")
import pandas as pd
from pandas import DataFrame
from air_pollution.common.entities import AqPrediction, AirQuality
from air_pollution.common.repositories import PredictionRepository


def get_aq_station_names():
    """
    Retrieves all aq_station_ids from json_file, as these are used as station_ids in X_train, y_train, X_test and y_test.
    :return: station_names as set.
    """
    with io.open("../../../air_pollution/resources/map_aq2station.json") as f:
        data = json.load(f)
        station_names = set(data.keys())
        return station_names


def get_frames_for_station_of_datapart_2_frame(station_id, datapart_2_frame):
    """
    :param station_id: string with station_id, for which dataFrames are needed.
    :param datapart_2_frame: dictionary mapping datapart to frame, e.g. mapping X_train to its corresponding
    dataFrame containing data of all stations
    :return: dataFrames X_train, y_train, X_test, y_test,for station_id
    """
    X_train = datapart_2_frame['X_train'].groupby('station_id').get_group(station_id)
    y_train = datapart_2_frame['y_train'].groupby('station_id').get_group(station_id)
    X_test = datapart_2_frame['X_test'].groupby('station_id').get_group(station_id)
    y_test = datapart_2_frame['y_test'].groupby('station_id').get_group(station_id)
    return X_train, y_train, X_test, y_test


def prepare_X_and_y(X, y):
    """
    Prepares feature and target frames by removing unnecessary columns,
    transforming into numpy arrays and reshaping.
    :param X: dataFrame containing feature data.
    :param y: dataFrame containing target data (already data of 48 hours per row).
    :return: X: np.array (day, hours*feat) and y: np. array (day, hours*target_values)
    """
    X_cleaned, y_cleaned = remove_unnecessary_cols(X, y)
    X_3d, y_3d = reshape_frame_to_3d_array(X_cleaned), reshape_frame_to_3d_array(y_cleaned)
    X_2d, y_2d = reshape_array_to_2d(X_3d), reshape_array_to_2d(y_3d)
    return X_2d ,y_2d


def remove_id_and_timestamp_from_frame(dataframe):
    """
    If station_id and timestamp are present in a dataframe, they will be removed.
    :param dataframe:
    :return: dataframe without station_id and timestamp columns.
    """
    if 'station_id' in dataframe.columns.values:
        dataframe.drop(['station_id'], axis=1, inplace=True)
    if 'timestamp' in dataframe.columns.values:
        dataframe.drop(['timestamp'], axis=1, inplace=True)
    return dataframe



def remove_unnecessary_cols(X, y):
    """
    Removes station_id and timestamp from dataframes as they should not be contained in the later
    feature and target arrays.
    :param X: dataFrame containing feature data of training set
    :param y: dataFrame containing prediction data of training set
    :param X, y: dataFrames without timestamp and station_id column
    """
    X = remove_id_and_timestamp_from_frame(X)
    y = remove_id_and_timestamp_from_frame(y)
    return X, y


def reshape_frame_to_3d_array(frame):
    """
    Reshapes dataFrame containing several days into 3d numpy array, where
    the number of days will be encoded in the depth dimension.
    :param frame:  dataFrame: (hours, feature_columns) or (hours, prediction_values)
    :return: result: numpy array: (days, hours, feature_columns)
    """
    array = frame.values
    rows_count, col_count = array.shape
    n_samples = rows_count // 24
    result = np.reshape(array, (int(n_samples), 24, col_count))
    return result


def reshape_array_to_2d(array):
    """
    Reshapes 3d array (days, hours, columns) to (days, hours*columns)
    :param array: numpy 3d array (days, hours*columns)
    :return: result: numpy 3d array (days, hours*columns)
    """
    number_new_rows = array.shape[0]
    number_new_cols = 24 *array.shape[2]
    result = np.reshape(array, (number_new_rows, number_new_cols))
    return result
