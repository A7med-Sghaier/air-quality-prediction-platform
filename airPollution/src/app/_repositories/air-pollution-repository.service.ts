import {Injectable} from '@angular/core';
import {WeatherService} from '../_services/weather.service';
import {Station} from '../_models/Station';
import {Observable} from 'rxjs/internal/Observable';
import {AirPollution} from '../_models/AirPollution';
import {map} from 'rxjs/operators';

export interface AirPollutionData {
  pm25: number[];
  pm10: number[];
  no2: number[];
  o3: number[];
  so2: number[];
  co: number[];
  airPollutionDates: number[];
}

@Injectable({
  providedIn: 'root'
})
export class AirPollutionRepositoryService {
  constructor(private weatherService: WeatherService) {
  }

  getAirPollutionDataForStation(station: Station): Observable<AirPollution[]> {
    return this.weatherService.getAirPollutionHistory(station._id);
  }

  getTimeMappedAirPollutionData(station: Station): Observable<AirPollutionData> {
    return this.getAirPollutionDataForStation(station)
      .pipe(
        map(x => this.prepareAirPollutionData(x))
      );
  }

  private prepareAirPollutionData(airPollution: AirPollution[]): AirPollutionData {
    const res: AirPollutionData = this.createAirPollutionDataObject();
    res.o3 = airPollution.map(result => result.o3);
    res.pm25 = airPollution.map(result => result.pm25);
    res.pm10 = airPollution.map(result => result.pm10);
    res.no2 = airPollution.map(result => result.no2);
    res.so2 = airPollution.map(result => result.so2);
    res.co = airPollution.map(result => result.co);
    res.airPollutionDates = airPollution.map(result => result.timestamp.getTime());

    return res;
  }

  public createAirPollutionDataObject(): AirPollutionData {
    return {
      pm25: [],
      pm10: [],
      no2: [],
      o3: [],
      so2: [],
      co: [],
      airPollutionDates: [],
    };
  }
}
