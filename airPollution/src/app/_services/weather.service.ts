import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs/internal/Observable';

import {UrlBuilder} from '../_helpers/http-req-builder';
import {map} from 'rxjs/operators';
import {Station, StationRaw, StationType} from '../_models/Station';
import {City} from '../_models/City';
import {AirPollution, AirPollutionRaw} from '../_models/AirPollution';
import {Prediction, PredictionRaw, Predictor, PredictorRaw} from '../_models/predictors';
import {Weather, WeatherRaw} from '../_models/Weather';
import {ErrorMetricRaw, ErrorMetricValueRaw} from '../_models/ErrorMetric';

@Injectable()
export class WeatherService {
  constructor(private _http: HttpClient, private urlBuilder: UrlBuilder) {
  }

  getStationsForCity(city: City): Observable<Station[]> {
    const url = this.urlBuilder.buildRequestUrl(`/cities/${city.name}/stations`);
    return this._http.get(url)
      .pipe(
        map((x: any): StationRaw[] => x),
        map(x => this.createStationsFromJson(x))
      );
  }

  private createStationsFromJson(json: StationRaw[]): Station[] {
    const result: Station[] = [];

    for (const row of json) {
      const station = new Station();
      station._id = row._id.$oid;
      station.name = row.name;
      station.stationType = this.createStationTypeFromString(row.station_type);
      station.longitude = row.longitude;
      station.latitude = row.latitude;
      station.city = row.city;
      station.location_type = row.location_type;
      station.is_grid = row.is_grid;
      station.need_prediction = row.need_prediction;
      result.push(station);
    }

    return result;
  }

  private createStationTypeFromString(stationType: string): StationType {
    switch (stationType.toLowerCase()) {
      case 'aq':
        return StationType.AQ;
      default:
        return StationType.MEO;
    }
  }

  getWeatherHistory(station_id, isGridStation): Observable<Weather[]> {
    const url = this.urlBuilder.buildRequestUrl('/stations/' + station_id + '/weather-measurements/' + isGridStation);
    return this._http.get(url)
      .pipe(
        map((x: any): WeatherRaw[] => x),
        map(x => this.createWeatherFromJson(x))
      );
  }

  private createWeatherFromJson(json: WeatherRaw[]): Weather[] {
    const result: Weather[] = [];

    for (const row of json) {
      const weather = new Weather();
      weather.humidity = row.humidity;
      weather.pressure = row.pressure;
      weather.temperature = row.temperature;
      weather.wind_speed = row.wind_speed;
      weather.wind_dire = row.wind_dire;
      weather.weather = row.weather;
      weather.timestamp = new Date(row.timestamp.$date);

      result.push(weather);
    }

    return result;
  }

  getAirPollutionHistory(station_id): Observable<AirPollution[]> {
    const url = this.urlBuilder.buildRequestUrl('/stations/' + station_id + '/air-quality');
    return this._http.get(url)
      .pipe(
        map((x: any): AirPollutionRaw[] => x),
        map(x => this.createAirPollutionsFromJson(x))
      );
  }

  private createAirPollutionsFromJson(json: AirPollutionRaw[]): AirPollution[] {
    const result: AirPollution[] = [];

    for (const row of json) {
      result.push(this.createAirPollutionFromJson(row));
    }

    return result;
  }

  public createAirPollutionFromJson(row: AirPollutionRaw): AirPollution {
    const airPollution = new AirPollution();

    airPollution.pm25 = row.pm25;
    airPollution.pm10 = row.pm10;
    airPollution.no2 = row.no2;
    airPollution.co = row.co;
    airPollution.o3 = row.o3;
    airPollution.so2 = row.so2;
    airPollution.timestamp = new Date(row.timestamp.$date);

    return airPollution;
  }

  getPredictions(stationId: string, predictorName: string): Observable<Prediction[]> {
    const url = this.urlBuilder.buildRequestUrl(`/stations/${stationId}/predictions/${predictorName}`);
    return this._http.get(url)
      .pipe(
        map((x: any): PredictionRaw[] => x),
        map(x => this.createPredictionsFromJson(x))
      );
  }

  private createPredictionsFromJson(json: PredictionRaw[]): Prediction[] {
    const result: Prediction[] = [];

    for (const row of json) {
      // todo:
      row.air_quality.timestamp = row.utc_time;
      const prediction = new Prediction();

      prediction.id = row._id.$oid;
      prediction.predictionType = row.prediction_type;
      prediction.stationName = row.station_name;
      prediction.timestamp = new Date(row.utc_time.$date);
      prediction.airQuality = this.createAirPollutionFromJson(row.air_quality);

      result.push(prediction);
    }

    return result;
  }

  public getPredictors(): Observable<Predictor[]> {
    const url = this.urlBuilder.buildRequestUrl('/predictors/');
    return this._http.get<PredictorRaw[]>(url)
      .pipe(
        map(x => this.createPredictorsFromJson(x))
      );
  }

  private createPredictorsFromJson(raw: PredictorRaw[]): Predictor[] {
    const result: Predictor[] = [];

    for (const row of raw) {
      const predictor = new Predictor();
      predictor.name = row.name;
      result.push(predictor);
    }

    return result;
  }

  public getAllMetrics(): Observable<ErrorMetricRaw[]> {
    const url = this.urlBuilder.buildRequestUrl('/metrics');
    return this._http.get<ErrorMetricRaw[]>(url);
  }

  public getMetricsByStationName(predictor: string, stationName: string): Observable<ErrorMetricValueRaw[]> {
    const url = this.urlBuilder.buildRequestUrl(`/predictors/${predictor}/metrics/${stationName}`);
    return this._http.get<ErrorMetricValueRaw[]>(url);
  }
}
