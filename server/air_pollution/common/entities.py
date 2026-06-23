
class AirQuality(object):
    def __init__(self, pm25, pm10, no2, co, o3, so2):
        """
        basic structure of air quality. It consist of pm 2.5, pm 1.0, NO2, CO, O3, SO2
        """
        self.pm25 = None if pm25 == "" else float(pm25)
        self.pm10 = None if pm10 == "" else float(pm10)
        self.no2 = None if no2 == "" else float(no2)
        self.co = None if co == "" else float(co)
        self.o3 = None if o3 == "" else float(o3)
        self.so2 = None if so2 == "" else float(so2)

    def print_parameters(self):
        """
        print this air quality.
        """
        print('pm25: ', self.pm25, end='\t')
        print('pm10: ', self.pm10, end='\t')
        print('no2: ', self.no2, end='\t')
        print('co: ', self.co, end='\t')
        print('co3: ', self.o3, end='\t')
        print('so2: ', self.so2, end='\t')


class AqHistory(object):
    def __init__(self, utc_time, air_quality=None):
        """
        basic structure of air quality history. It contains a utc_time and a object of air quality. 
        """
        self.utc_time = utc_time
        self.air_quality = air_quality


class AqPrediction(object):
    def __init__(self, station_name, utc_time, prediction_type, config=None, air_quality=None, is_first_day=True):
        self.station_name = station_name
        self.utc_time = utc_time
        self.prediction_type = prediction_type
        self.air_quality = air_quality
        self.is_first_day = is_first_day
        self.config = config

class MeHistory(object):
    def __init__(self, utc_time, meteo=None):
        """
        basic structure of Meteo meteorological data history. It contains a utc_time and a object of Meteo. 
        """
        self.utc_time = utc_time
        self.meteo = meteo


class HistoryGrid(object):
    def __init__(self, utc_time, meteo_grid=None, air_quality=None):
        """
        basic structure of grid. The grid has the meteorological data in geographical position (wkith latitude and longitude)
        """
        self.utc_time = utc_time
        self.meteo_grid = meteo_grid
        self.air_quality = air_quality


class Meteo(object):

    def __init__(self, temperature, pressure, humidity, wind_dire, wind_speed, weather=None):

        """
        basic structure of Meteo. Actually, it is made up of various meteorological data.
        These meteorological data include temperature, pressure, and so on.
        """
        self.temperature = None if temperature == "" else float(temperature)
        self.pressure = None if pressure == "" else float(pressure)
        self.humidity = None if humidity == "" else float(humidity)
        self.wind_dire = None if wind_dire == "" else float(wind_dire)
        self.wind_speed = None if wind_speed == "" else float(wind_speed)
        self.weather = weather

    def print_parameters(self):
        """
        print the meteorological data of this meteo.
        """
        print("temperat: ", self.temperat, end='\t')
        print("pressure: ", self.pressure, end='\t')
        print("humidity: ", self.humidity, end='\t')
        print("wind_speed: ", self.wind_speed, end='\t')
        if self.weather:
            print("weather: ", self.weather, end='\t')


class Station(object):

    def __init__(self, name, longitude=None, latitude=None, city=None, location_type=None, is_grid=False, station_type='aq', need_prediction=True):
        """
        basic structure of station. We use city to show which city this station belongs.
        If we use the grid data to predict this station's air quality, the variable "is_grid" is true, and
        we use me_grid_histories to store these data.
        If we use the meteo data, the the variable "is_grid" is false, and we use me_histories to store some data.
        """
        self.name = name
        self.station_type = station_type
        self.longitude = None if not longitude else float(longitude)
        self.latitude = None if not latitude else float(latitude)
        self.city = city
        self.location_type = location_type
        self.is_grid = is_grid
        self.need_prediction = need_prediction
        self.aq_histories = []
        self.me_histories = []
        self.me_grid_histories = []

    def append_aq_history(self, history):
        self.aq_histories.append(history)

    def append_me_history(self, history):
        self.me_histories.append(history)

    def append_me_grid_history(self, history):
        self.me_grid_histories.append(history)

    def print_parameters(self):
        """
        print the basic infomation of this station.
        """
        print("id: ", self.id, end='\t')
        print("longitude: ", self.longitude, end='\t')
        print("latidude: ", self.latitude, end='\t')
        print("city: ", self.city, end='\t')
        if self.location_type:
            print("location_type: ", self.location_type, end='\t')
        print("is_grid: ", self.is_grid, end='\t\n')
        print("histories: ", self.histories, end='\t')
