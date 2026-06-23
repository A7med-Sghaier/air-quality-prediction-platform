"""
***********************************************
* DataSc - historyExtractor
* created by : AHMED SGHAIER
* created on : 30.04.18 - 13:21
* copyright : all right reserved @LMU 2018
***********************************************
"""
import urllib3 as url_helper
import pandas as pd
from dateutil.parser import parse

from air_pollution.common.entities import Station, AirQuality, Meteo, AqHistory, MeHistory
from air_pollution.common.repositories import StationsRepository


class HistoryExtractor:
    def __init__(self, city_alias):
        self.city_alias = city_alias
        self.ref_key = "2k0d1d8"
        self.stationRepository = StationsRepository()

    def extract_air_quality_data(self, start_time, end_time):
        data = self.get_api_data("airquality", start_time, end_time)
        df = self.convert_data_to_pandas(data)
        return df

    def extract_meteorology_data(self, start_time, end_time):
        data = self.get_api_data("meteorology", start_time, end_time)
        df = self.convert_data_to_pandas(data)
        print("get me data dataframe, shape : " + str(df.shape))
        return df

    def extract_meteorology_grid_data(self, start_time, end_time):
        data = self.get_api_data("meteorology", start_time, end_time, grid="_grid")
        df = self.convert_data_to_pandas(data, grid=True)
        print("get me grid data dataframe, shape : " + str(df.shape))
        return df

    def get_api_data(self, data_type, start_time, end_time, grid=""):
        url = "https://biendata.com/competition/" + str(data_type) + "/" + str(self.city_alias) + grid + "/" + str(
            start_time) + "/" + str(end_time) + "/" + str(self.ref_key)
        http = url_helper.PoolManager()
        req = http.request('GET', url)
        data = req.data.decode('utf-8').split('\r\n')
        return data

    def convert_data_to_pandas(self, data, grid=False):
        columns = data[0].split(',')
        if grid:
            data_body = list(map(lambda line: tuple(line.split(',')), data[1:]))
        else:
            data_body = list(map(lambda line: self.clean_non_grid_stations_id(line), data[1:]))

        df = pd.DataFrame(data_body, columns=columns)
        return df

    @staticmethod
    def clean_non_grid_stations_id(line):
        splited_line = line.split(',')
        #if len(splited_line) > 1 and '_' in splited_line[1]:
        #    index_of_sep = splited_line[1].index('_')
        #    splited_line[1] = splited_line[1][0:index_of_sep]
        return tuple(splited_line)

    @staticmethod
    def build_air_quality(values, index):
        pm25 = values['PM25_Concentration'][index] if 'PM25_Concentration' in values.columns.values and \
                                                      values['PM25_Concentration'][index] != "NaN" else ""
        pm10 = values['PM10_Concentration'][index] if 'PM10_Concentration' in values.columns.values and \
                                                      values['PM10_Concentration'][index] != "NaN" else ""
        no2 = values['NO2_Concentration'][index] if 'NO2_Concentration' in values.columns.values and \
                                                    values['NO2_Concentration'][index] != "NaN" else ""
        co = values['CO_Concentration'][index] if 'CO_Concentration' in values.columns.values and \
                                                  values['CO_Concentration'][index] != "NaN" else ""
        o3 = values['O3_Concentration'][index] if 'O3_Concentration' in values.columns.values and \
                                                  values['O3_Concentration'][index] != "NaN" else ""
        so2 = values['SO2_Concentration'][index] if 'SO2_Concentration' in values.columns.values and \
                                                    values['SO2_Concentration'][index] != "NaN" else ""

        return AirQuality(pm25=pm25, pm10=pm10, no2=no2, co=co, o3=o3, so2=so2)

    @staticmethod
    def build_meteo(values, index):
        weather = values['weather'][index] if 'weather' in values.columns.values and values['weather'][
            index] != "NaN" else ""
        temperature = values['temperature'][index] if 'temperature' in values.columns.values and values['temperature'][
            index] != "NaN" else ""
        pressure = values['pressure'][index] if 'pressure' in values.columns.values and values['pressure'][
            index] != "NaN" else ""
        humidity = values['humidity'][index] if 'humidity' in values.columns.values and values['humidity'][
            index] != "NaN" else ""
        wind_speed = values['wind_speed'][index] if 'wind_speed' in values.columns.values and values['wind_speed'][
            index] != "NaN" else ""
        wind_direction = values['wind_direction'][index] if 'wind_direction' in values.columns.values and \
                                                            values['wind_direction'][index] != "NaN" else ""

        return Meteo(temperature=temperature, pressure=pressure, humidity=humidity, wind_dire=wind_direction,
                     wind_speed=wind_speed, weather=weather)

    def persist_histories(self, data_frame, history_label):
        if data_frame.empty:
            print("persist a empty data_frame")
            return

        groups = data_frame.groupby("station_id")

        print("insert " + history_label + " into Mongdb")

        for key, values in groups:
            station = Station(key)
            for index in values.index.values:

                time = values['time'][index] if values['time'][index] else ""

                if history_label == "aq":
                    airq = self.build_air_quality(values, index)
                    history = AqHistory(utc_time=parse(time), air_quality=airq.__dict__)
                    station.append_aq_history(history.__dict__)

                elif history_label == "me":
                    meteo = self.build_meteo(values, index)
                    history = MeHistory(utc_time=parse(time), meteo=meteo.__dict__)
                    station.append_me_history(history.__dict__)

                elif history_label == "me_grid":
                    meteo = self.build_meteo(values, index)
                    history = MeHistory(utc_time=parse(time), meteo=meteo.__dict__)
                    station.append_me_grid_history(history.__dict__)

            self.stationRepository.add_station_history(station.__dict__, history_label)
