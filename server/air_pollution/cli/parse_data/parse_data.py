#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

from data_classes.station import Station
from data_classes.history_grid import HistoryGrid
from data_classes.history import History
from data_classes.air_quality import AirQuality
from data_classes.meteo import Meteo
from collections import defaultdict
import csv
import argparse
import io



def read_bejing_station_file(filepath):
    lines = []
    with io.open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    location_types = ["Urban Stations", "Suburban Stations", "Other Stations", "Stations Near Traffic"]
    id_to_station = get_id_to_station(lines, location_types)
    return id_to_station



def get_id_to_station(lines, location_types):
    start_index = lines.index("Urban Stations") + 1
    location_type = location_types[0][:-1]
    id_to_station = {}
    for line in lines[start_index:]:
        if line not in location_types:
            splitted = line.split("\t")
            station_id = splitted[0]
            longitude = splitted[1]
            latitude = splitted[2]
            station = Station(station_id, longitude, latitude, location_type=location_type)
            id_to_station[station_id] = station
        elif line in location_types:
            location_type = line[0][:-1]
    return id_to_station



def read_meteo_data(filepath):
    id_to_lines = defaultdict(list)
    with io.open(filepath) as f:
    #station_id,longitude,latitude,utc_time,temperature,pressure,humidity,wind_direction,wind_speed,weather
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if not row[0] == 'station_id':
                id_to_lines[row[0]].append(row)
        id_to_time_to_meteo = get_id_to_time_to_meteo(id_to_lines, has_weather=True)
    return id_to_time_to_meteo



def get_id_to_time_to_meteo(id_to_lines, has_weather=False):
    id_to_time_to_meteo = defaultdict(dict)
    for id, lines in id_to_lines.items():
        #print("id: ", id)
        for i, line in enumerate(lines):
            #print("i: ", i)
            time = line[3]
            if has_weather==True:
                meteo = Meteo(line[4], line[5], line[6],line[7], line[8], weather=line[9])
            else:
                meteo = Meteo(line[4], line[5], line[6],line[7], line[8])
            id_to_time_to_meteo[id][time] = meteo
    return id_to_time_to_meteo



def read_meteo_grid_file(filepath):
    id_to_station_grid = {}
    id_to_lines = defaultdict(list)
    with io.open(filepath) as f:
        reader = csv.reader(f)
        for row in reader:
            if not row[0] == 'stationName':
                #print(row)
                station = Station(id, row[1], row[2], is_grid=True)
                id_to_station_grid[id] = station
                id_to_lines[row[0]].append(row)
        id_to_time_to_meteo_grid = get_id_to_time_to_meteo(id_to_lines)
    return id_to_station_grid, id_to_time_to_meteo_grid


def read_air_quality(filepath):
    # stationId     utc_time    PM2.5   PM10    NO2 CO  O3  SO2
    id_to_time_to_aq = defaultdict(dict)
    with io.open(filepath) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] != 'stationId':
                id = row[0]
                time = row[1]
                air_quality = AirQuality(row[2], row[3], row[4], row[5], row[6], row[7])
                id_to_time_to_aq[id][time] = air_quality
    return id_to_time_to_aq


def get_stations_objects(id_to_station, id_to_time_to_meteo, id_to_time_to_aq, is_grid=False):
    stations = []
    for id,station in id_to_station.items():
        time_to_meteo = id_to_time_to_meteo.get(id)
        time_to_aq = id_to_time_to_aq.get(id)
        times = get_times(time_to_meteo, time_to_aq)
        for time in times:
            if is_grid and time_to_meteo:
                history = History(time, meteo_grid=time_to_meteo.get(time), air_quality=id_to_time_to_aq[time])
                station.append_history(history)
            elif not is_grid and time_to_meteo:
                history = History(time, meteo=time_to_meteo.get(time), air_quality=id_to_time_to_aq[time])
                station.append_history(history)
        stations.append(station)
    return stations


def get_times(time_to_meteo, time_to_aq):
    times = []
    if time_to_meteo and time_to_aq:
        times = time_to_aq.keys() + time_to_meteo.keys()
    elif time_to_meteo and not time_to_aq:
        times = time_to_meteo
    elif time_to_aq and not time_to_meteo:
        times = time_to_aq
    return set(times)




if __name__ == '__main__':
    id_to_station = read_bejing_station_file('resources/bejing/Bejing_AirQuality_Stations.txt')
    print("Finished reading Bejing stations file.")
    id_to_time_to_meteo = read_meteo_data('resources/bejing/beijing_17_18_meo.csv')
    print("Finished reading meteo file.")
    id_to_station_grid, id_to_time_to_meteo_grid = read_meteo_grid_file('resources/bejing/Beijing_historical_meo_grid.csv')
    print("Finished reading meteo grid file.")
    id_to_time_to_aq = read_air_quality('resources/bejing/beijing_17_18_aq.csv')
    print("Finished reading air quality file.")
    stations = get_stations_objects(id_to_station, id_to_time_to_meteo, id_to_time_to_aq)
    print("Finished creating station objects for non grid data.")
    stations_grid = get_stations_objects(id_to_station_grid, id_to_time_to_meteo_grid, id_to_time_to_aq)
    print("Finished creating station objects for grid data.")
    for station in stations_grid:
        station.print_parameters()
