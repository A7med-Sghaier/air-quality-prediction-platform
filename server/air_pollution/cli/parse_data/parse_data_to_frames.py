import io
import pandas
import numpy as np



def read_bejing_station_file(filepath):
    """

    :param filepath:
    :return:
    """
    lines = []
    with io.open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    location_types = ["Urban Stations", "Suburban Stations", "Other Stations", "Stations Near Traffic"]
    id_to_station = get_id_to_station(lines, location_types)
    return id_to_station




def get_id_to_station(lines, location_types):
    """

    :param lines:
    :param location_types:
    :return:
    """
    start_index = lines.index("Urban Stations")+1
    location_type = location_types[0][:-1]
    id_to_location_type = {}
    for line in lines[start_index:]:
        if line not in location_types:
            splitted = line.split("\t")
            station_id = splitted[0]
            id_to_location_type[station_id] = location_type
        elif line in location_types:
            location_type = line.replace("Stations", "Station")
    return id_to_location_type


def get_meteo_table(filepath, id_to_location_type):
    """

    :param filepath:
    :param id_to_location_type:
    :return:
    """
    meteo_table = pandas.read_csv(filepath, sep=',')
    meteo_table['location_type'] = meteo_table.apply \
        (lambda row: id_to_location_type[row.station_id] if row.station_id in id_to_location_type else np.nan, axis=1)
    print(meteo_table)
    return meteo_table


if __name__ == '__main__':
    id_to_location_type = read_bejing_station_file('resources/bejing/Beijing_AirQuality_Stations_en.txt')
    # station_id,longitude,latitude,utc_time,temperature,pressure,humidity,wind_direction,wind_speed,weather
    meteo_table = get_meteo_table('resources/bejing/beijing_17_18_meo.csv', id_to_location_type)
    grid_table = pandas.read_csv('resources/bejing/Beijing_historical_meo_grid.csv', sep = ',')
    air_quality_table = pandas.read_csv('resources/bejing/beijing_201802_201803_aq.csv', sep=',')

    #data for london
    meteo_table_grid = pandas.read_csv('resources/london/London_historical_meo_grid.csv', sep=',')
    aq_forecast_stations = pandas.read_csv('resources/london/London_historical_aqi_forecast_stations_20180331.csv', sep=',')
    aq_other_stations = pandas.read_csv('resources/london/London_historical_aqi_other_stations_20180331.csv', sep=',')




