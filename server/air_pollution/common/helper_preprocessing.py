from math import sin, cos, radians, pi, asin, sqrt
from sklearn.preprocessing import LabelEncoder
import numpy as np


class ColumnsLabelEncoder:
    def __init__(self, columns=None):
        self.columns = columns  # array of column names to encode

    def fit(self, X, y=None):
        return self

    def transform(self, data):
        if self.columns is not None:
            for col in self.columns:
                data[col] = LabelEncoder().fit_transform(data[col])
        else:
            for colname, col in data.iteritems():
                data[colname] = LabelEncoder().fit_transform(col)
        return data

    def fit_transform(self, data, y=None):
        return self.fit(data, y).transform(data)


def normalize_cyclical_features(dataframe, remove_old=True):
    """
    Normalizes all cyclical features by calling other functions.
    Cyclical features: wind_direction, hour and month.
    :param     dataframe: dataframe with wind_dire, hour and month
    :param:   remove_old: old sequential representations are deleted by default True.
    :return:   dataframe with normalized features (e.g. hour.sin and hour.cos)
                Original features like hour still contained for debugging reasons.
    """
    dataframe = normalize_wind_dire(dataframe, remove_old)
    dataframe = normalize_month(dataframe, remove_old)
    dataframe = normalize_hour(dataframe, remove_old)

    return dataframe




def normalize_wind_dire(dataframe, remove_old=True):
    """
    Normalize wind direction in dataframe   to represent circular structure of wind_direction values.
    (360 and 0 degree are the same, 1 degree and 360 are neighbours to each other despite of
    being farthest from each other in range of values.)
    :param:   dataframe that contains wind_dire column
    :param:   remove_old: old sequential representation of wind_dire is deleted by default True.
    :return:  dataframe containing wind_dire encoded in wind_dire.sin and wind_dir.cos columns
    """

    dataframe.wind_dire=np.array(dataframe.wind_dire,dtype=float)
    dataframe['wind_dire_sin'] = np.sin(dataframe.wind_dire * (2. * np.pi / 360.0))
    dataframe['wind_dire_cos'] = np.cos(dataframe.wind_dire * (2. * np.pi / 360.0))
    if remove_old:
        dataframe.pop('wind_dire')
    return dataframe


def normalize_month(dataframe, remove_old=True):
    """
    Normalize month in dataframe to represent circular structure of time.
    :param:    dataframe that contains month column
    :param:   remove_old: old sequential representation of month is deleted by default True.
    :return:   dataframe containing month encoded in month_sin and month_cos columns
    """

    dataframe.month=np.array(dataframe.month,dtype=float)
    dataframe['month_sin'] = np.sin(dataframe.month * (2. * np.pi / 12))
    dataframe['month_cos'] = np.cos(dataframe.month * (2. * np.pi / 12))
    if remove_old:
        dataframe.pop('month')
    return dataframe


def normalize_hour(dataframe, remove_old=True):
    """
    Normalize month in dataframe to represent circular structure of time.
    :param   dataframe that contains hour column
    :param:   remove_old: old sequential representation of month is deleted by default True.
    :return: dataframe containing month encoded in hour_sin and hour_cos columns
    """

    dataframe.hour = np.array(dataframe.hour,dtype=float)
    dataframe['hour_sin'] = np.sin(dataframe.hour * (2. * np.pi / 24))
    dataframe['hour_cos'] = np.cos(dataframe.hour * (2. * np.pi / 24))
    if remove_old:
        dataframe.pop('hour')
    return dataframe


def haversine(station_loc_1, station_loc_2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    :param      station_loc_1: list containing longitude and latitude for point 1
    :param      station_loc_2: list containing longitude and latitude for point 2
    :return:    float circle distance: c*r
    """
    lat1 = station_loc_1[0]
    lon1 = station_loc_1[1]
    lat2 = station_loc_2[0]
    lon2 = station_loc_2[1]
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def append_day_in_month_column(dataframe):
    pass


def append_day_in_week_column(datafrane):
    pass


def append_is_working_day_column(holiday_set, dataframe):
    pass


def get_holidays(is_beijing=True):
    holiday_set = set()
    if is_beijing:
        holiday_set = get_beijing_holidays(beijing_file)
    else:
        holiday_set = extract_london_holidays(london_file)
    return holiday_set


def get_beijing_holidays(beijing_file):
    pass


def get_london_holidays(london_file):
    pass
