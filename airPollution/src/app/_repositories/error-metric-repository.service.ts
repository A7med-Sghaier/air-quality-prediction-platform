import {Injectable} from '@angular/core';
import {Observable} from 'rxjs/internal/Observable';
import {ErrorMetric, ErrorMetricRaw, ErrorMetricValue, ErrorMetricValueRaw} from '../_models/ErrorMetric';
import {WeatherService} from '../_services/weather.service';
import {map} from 'rxjs/operators';
import {Station} from '../_models/Station';
import {Predictor} from '../_models/predictors';

@Injectable({
  providedIn: 'root'
})
export class ErrorMetricRepositoryService {

  constructor(private weatherService: WeatherService) {
  }

  public getAll(): Observable<ErrorMetric[]> {
    return this.weatherService.getAllMetrics()
      .pipe(
        map(x => this.createErrorMetricsFromRaw(x))
      );
  }

  private createErrorMetricsFromRaw(errorMetricsRaw: ErrorMetricRaw[]): ErrorMetric[] {
    const res: ErrorMetric[] = [];

    for (const errorMetricRaw of errorMetricsRaw) {
      res.push(this.createErrorMetricFromRaw(errorMetricRaw));
    }

    return res;
  }

  private createErrorMetricFromRaw(errorMetricRaw: ErrorMetricRaw): ErrorMetric {
    const errorMetric = new ErrorMetric();
    errorMetric.key = errorMetricRaw.key;
    errorMetric.name = errorMetricRaw.name;
    errorMetric.short = errorMetricRaw.short;
    return errorMetric;
  }

  public getMetricsByStation(predictor: Predictor, station: Station): Observable<ErrorMetricValue[]> {
    return this.weatherService.getMetricsByStationName(predictor.name, station.name)
      .pipe(
        map(x => this.createErrorMetricValuesFromRaw(x))
      );
  }

  private createErrorMetricValuesFromRaw(errorMetricsRaw: ErrorMetricValueRaw[]): ErrorMetricValue[] {
    const res: ErrorMetricValue[] = [];

    for (const errorMetricRaw of errorMetricsRaw) {
      res.push(this.createErrorMetricValueFromRaw(errorMetricRaw));
    }

    return res;
  }

  private createErrorMetricValueFromRaw(errorMetricRaw: ErrorMetricValueRaw): ErrorMetricValue {
    const errorMetric = new ErrorMetricValue();

    errorMetric.name = errorMetricRaw.name;
    errorMetric.type = errorMetricRaw.type;
    errorMetric.airPollution = {
      pm25: errorMetricRaw.values.pm25,
      pm10: errorMetricRaw.values.pm10,
      no2: errorMetricRaw.values.no2,
      co: errorMetricRaw.values.co,
      o3: errorMetricRaw.values.o3,
      so2: errorMetricRaw.values.so2,
    };

    return errorMetric;
  }
}
