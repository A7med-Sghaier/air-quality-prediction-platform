import { Injectable } from '@angular/core';
import { WeatherService } from '../_services/weather.service';
import { Station } from '../_models/Station';
import { Observable } from 'rxjs/internal/Observable';
import { Weather, WeatherData } from '../_models/Weather';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class WeatherRepositoryService {
  constructor(private weatherService: WeatherService) {
  }

  public getWeatherHistoryForStation(station: Station): Observable<Weather[]> {
    return this.weatherService.getWeatherHistory(station._id, station.is_grid);
  }

  public getMappedWeatherHistory(station): Observable<WeatherData> {
    return this.getWeatherHistoryForStation(station)
      .pipe(
        map(x => this.prepareWeatherData(x))
      );
  }

  private prepareWeatherData(weather: Weather[]): WeatherData {
    const weatherData: WeatherData = new WeatherData();

    weatherData.temperature = weather.map(result => result.temperature);
    weatherData.pressure = weather.map(result => result.pressure);
    weatherData.humidity = weather.map(result => result.humidity);
    weatherData.wind = weather.map(result => result.wind_speed);
    weatherData.windDirections = weather.map(result => result.wind_dire);
    weatherData.weatherDates = weather.map(result => result.timestamp.getTime());
    weatherData.weather = weather.map(result => {
      let symbole = '15';
      switch (result.weather) {
        case 'Sunny/clear':
          symbole = '01d';
          break;
        case 'Hail':
          symbole = '13';
          break;
        case 'Light Rain':
          symbole = '01d';
          break;
        case 'Cloudy':
          symbole = '04';
          break;
        case 'Thundershower':
          symbole = '11';
          break;
        case 'Overcast':
          symbole = '02d';
          break;
        case 'Sleet':
          symbole = '12';
          break;
        case 'Rain':
          symbole = '10';
          break;
        case 'Fair':
          symbole = '02n';
          break;
        default:
          symbole = '15';
      }
      return symbole;
    });
    return weatherData;
  }

  public createWeatherDataObject(): WeatherData {
    return new WeatherData();
  }
}
