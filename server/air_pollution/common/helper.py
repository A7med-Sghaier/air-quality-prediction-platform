import dateutil.parser as date_util
import math

from air_pollution.common.entities import AirQuality

KEYS = ['pm25', 'pm10', 'no2', 'co', 'o3', 'so2']


def fill_up_air_pollution_keys(keys, values, default=0):
    """
    Ensure each requested air-quality key has a usable value.

    The legacy API mutates and returns the input dictionary, so callers that
    already hold a reference see the filled values.

    :param keys: a list of key
    :param values: the dictionary of key
    :param default: the default value of key
    :return: dictionary of key, and every key in these dictionary has a value. 
    """
    for key in keys:
        if key not in values or values[key] is None or _is_nan(values[key]):
            values[key] = default
    return values


def extract_air_quality_from_history(x):
    """
    transform the column named 'utc_time' to 'timestamp'
    utc_time: 12018/06/01  2:00:00
    timestamp:2018/06/01
    :param x: air quality data
    :return res: 
    """
    res = x['air_quality']
    res['timestamp'] = x['utc_time']
    return res


def extract_weather_data_from_history(x):
    """
    transform the column named 'utc_time' to 'timestamp'
    :param x: weather data, which  belongs to meteo or grid
    """
    res = x['meteo']
    res['timestamp'] = x['utc_time']
    return res


def parse_air_quality_for_prediction(index, x, station, city):
    """
    !!!deprecated!!!

    :param index:
    :param x:
    :param station:
    :param city:
    :return:
    """
    res = x['air_quality']

    res['PM2.5'] = res.pop('pm25')
    res['PM10'] = res.pop('pm10')
    res['O3'] = res.pop('o3')
    res['NO2'] = res.pop('no2')
    res['CO'] = res.pop('co')
    res['SO3'] = res.pop('so2')

    if city == 'London':
        res['O3'] = float(-1)

    res['timestamp'] = x['utc_time']
    res['hour'] = index
    res['month'] = x['utc_time'].datetime.month
    res['station_id'] = station
    res['test_id'] = str(str(res['station_id']) + "#" + str(index)).encode('utf-8').decode(
        'utf-8') if city == 'London' else str(str(res['station_id']) + "_aq#" + str(index))

    return res


def normalize_air_quality_for_prediction(x, station, city, latitude, longitude):
    """
    change the structure of air quality dataframe to be more friendly.
    we transform column 'utc_time' to 'month',  'hour' and 'timestamp'
    :param x: air quality data
    :param station: the station id
    :param city: beijing or london
    :param latitude:
    :param longitude:
    :return res:
    """
    res = x

    res['PM2.5'] = res.pop('pm25')
    res['PM10'] = res.pop('pm10')
    res['O3'] = res.pop('o3')
    res['NO2'] = res.pop('no2')
    res['CO'] = res.pop('co')
    res['SO2'] = res.pop('so2')


    if city == 'London':
        res['O3'] = float(-1)
    res['timestamp'] = x['utc_time'].date()
    res['month'] = x['utc_time'].month
    res['hour']= x['utc_time'].hour
    res['station_id'] = station
    res['latitude'] = latitude
    res['longitude'] = longitude
    return res


def normalize_meteo_for_prediction(x, station, latitude, longitude):
    """
    change the structure of meteo/grid dataframe to be more friendly.
    :param x: air quality data
    :param station: the station id
    :param city: beijing or london
    :param latitude:
    :param longitude:
    :return res:
    """
    res = x
    res['timestamp'] = x['utc_time'].strftime("%Y-%m-%d")
    res['month'] = x['utc_time'].month
    res['hour']= x['utc_time'].hour
    res['station_id'] = station
    res['latitude'] = latitude
    res['longitude'] = longitude
    # for value 977002
    if res['wind_dire'] > 362:
        res['wind_dire'] = 361.01
    res['station_id'] = station

    return res


def normalize_months(month):
    """
    convert month (01 ~ 12) to math represention.
    :param month: 01 ~ 12
    :return sin, cos: use the math represention.
    """
    sin = math.sin((((month % 12)/12.0)*360) * math.pi / 180.0)
    cos = math.cos((((month % 12)/12.0)*360) * math.pi / 180.0)
    return sin, cos




def convert_float_to_int(x):
    """
    convert float data to int data.
    """
    try:
        return str(int(float(x))).encode('utf-8').decode('utf-8')
    except ValueError:
        return str(x).replace('::', '').encode('utf-8').decode('utf-8')


def build_air_quality_for_prediction(values, index):
    """
    the try to use a empty string as the default value for these data who do not has value or the value is NaN
    :param values: the air quality data values
    :param index: the index of datafame
    :return : a data structure of AirQuality
    """
    pm25 = values['PM2.5'][index] if 'PM2.5' in values.columns.values and values['PM2.5'][index] != "NaN" else ""
    pm10 = values['PM10'][index] if 'PM10' in values.columns.values and values['PM10'][index] != "NaN" else ""
    o3 = values['O3'][index] if 'O3' in values.columns.values and values['O3'][index] != "NaN" else ""
    no2 = values['NO2'][index] if 'NO2' in values.columns.values and values['NO2'][index] != "NaN" else ""
    co = values['CO'][index] if 'CO' in values.columns.values and values['CO'][index] != "NaN" else ""
    so2 = values['SO2'][index] if 'SO2' in values.columns.values and values['SO2'][index] != "NaN" else ""

    return AirQuality(pm25=pm25, pm10=pm10, no2=no2, co=co, o3=o3, so2=so2)


def get_pipeline_map(histories_type, histories_selector):
    """Build the MongoDB projection stage that normalizes history arrays."""
    return {
        "$project": {
            "_id": "$_id",
            'name': "$name",
            'city': "$city",
            'latitude': "$latitude",
            'longitude': "$longitude",
            'histories': {
                "$map": {
                    "input": str("$" + histories_type),
                    "as": "history",
                    "in": {
                        "$mergeObjects": [
                            {
                                "utc_time": '$$history.utc_time'
                            },
                            str("$$history." + histories_selector)
                        ]
                    }
                }
            }
        }
    }


def get_pipline_map(histories_type, histories_selector):
    """Backward-compatible alias for the historical misspelled function name."""
    return get_pipeline_map(histories_type, histories_selector)


def get_pipeline_filter(last_date):
    """Build the MongoDB projection stage that filters histories by date."""
    return {
        "$project": {
            "_id": "$_id",
            'name': "$name",
            'city': "$city",
            'latitude': "$latitude",
            'longitude': "$longitude",
            'histories': {
                "$filter": {
                    "input": "$histories",
                    "as": "history",
                    "cond": {
                        "$gte":[{"$dateToString":{ "format": "%Y-%m-%d", "date":"$$history.utc_time"}} ,
                                {"$dateToString":{ "format": "%Y-%m-%d", "date":date_util.parse(last_date)}}]
                    }
                }
            }
        }
    }


def get_pipline_filter(lastDate):
    """Backward-compatible alias for the historical misspelled function name."""
    return get_pipeline_filter(lastDate)


def _is_nan(value):
    try:
        return math.isnan(value)
    except TypeError:
        return False
