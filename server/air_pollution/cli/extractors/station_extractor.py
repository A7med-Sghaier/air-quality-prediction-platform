"""
***********************************************
* DataSc - stationExtractor
* created by : AHMED SGHAIER
* created on : 27.04.18 - 15:41
* copyright : all right reserved @LMU 2018
***********************************************
"""
import codecs
import csv
import pandas as pd
import re
import openpyxl as px
import os
import inspect


from air_pollution.common.entities import Station
from air_pollution.common.repositories import StationsRepository


class StationExtractor:
    stations_repository = None

    def __init__(self):
        self.current_path = os.path.dirname( inspect.getfile(inspect.currentframe()))
        self.stations_repository = StationsRepository()
        self.reg_station_city = re.compile(r'(Stations at) (\w*)\t', re.MULTILINE)
        self.reg_station_pos = re.compile(r'(\w*) Stations', re.MULTILINE)
        self.reg_station_info = re.compile(r'(\w*)\t(\d*(\.\d*)?)\t(\d*(\.\d*)?)', re.MULTILINE)
        self.stations = list()

    def create_stations(self):
        self.extract_beijing_aq_stations()
        self.extract_beijing_meo_stations()
        self.extract_london_aq_stations()
        self.extract_grid_stations("bj")
        self.extract_grid_stations("ld")

        for station in self.stations:
            self.stations_repository.create_station(station.__dict__)
        print('end create Sttations')

    def extract_beijing_aq_stations(self):

        src_file = str(self.current_path)+'/../../resources/Beijing_AirQuality_Stations.xlsx'

        ws = px.load_workbook(filename=src_file)['Sheet1']
        city = None
        station_pos = None

        for row in ws.rows:
            line = ""
            for col in row:
                line += str(col.value) + "\t"

            find_city = self.reg_station_city.findall(line)
            find_station_pos = self.reg_station_pos.findall(line)
            find_station_info = self.reg_station_info.findall(line)

            if find_city:
                city = find_city[0][1]

            if find_station_pos:
                station_pos = find_station_pos[0]

            if find_station_info:
                find_station_info = find_station_info[0]
                station_id = find_station_info[0]
                station = Station(station_id, longitude=find_station_info[1],
                                  latitude=find_station_info[3], city=city,
                                  location_type=station_pos, station_type='aq')
                self.stations.append(station)

    def extract_beijing_meo_stations(self):
        src_file = str(self.current_path)+'/../../resources/beijing_17_18_meo.csv'
        with open(src_file, 'r') as meteo_file:
            reader = csv.DictReader(meteo_file)
            df = pd.DataFrame(list(reader), columns=['station_id', 'longitude', 'latitude']).drop_duplicates(keep='first')

            for row in df.values.tolist():
                station = Station(row[0], longitude=row[1], latitude=row[2],
                                  city="Beijing", need_prediction=False, station_type='meo')

                self.stations.append(station)

    def extract_london_aq_stations(self):
        src_file = str(self.current_path)+'/../../resources/London_AirQuality_Stations.csv'
        reader = codecs.open(src_file, 'r', 'utf-8', errors='ignore')
        reader.readline()
        for row in reader:
            row = row.strip().replace("\n", "").split(",")
            need_prediction = False if not row[2] else True
            station = Station(row[0], longitude=row[5], latitude=row[4], city="London",
                              location_type=row[6], need_prediction=need_prediction, station_type='aq')
            self.stations.append(station)

    def extract_grid_stations(self, city_alias):
        path =  None
        city = None
        if city_alias == "bj" :
            path = str(self.current_path)+'/../../resources/Beijing_grid_weather_station.csv'
            city = "beijing_grid"
        elif city_alias == "ld":
            path = str(self.current_path)+'/../../resources/London_grid_weather_station.csv'
            city = "london_grid"

        reader = codecs.open(path, 'r', 'utf-8', errors='ignore')
        for row in reader:
            row = row.strip().replace("\n", "").split(",")
            station = Station(row[0], latitude=row[1], longitude=row[2], city=city, is_grid=True, need_prediction=False, station_type='meo')
            self.stations.append(station)
            pass
