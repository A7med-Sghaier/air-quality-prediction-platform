import {Injectable} from '@angular/core';
import {WeatherService} from '../_services/weather.service';
import {Station} from '../_models/Station';
import {Observable} from 'rxjs/internal/Observable';
import {map} from 'rxjs/operators';
import {Prediction, Predictor} from '../_models/predictors';

export interface PredictionData {
  pm25: number[][];
  pm10: number[][];
  o3: number[][];
}

@Injectable({
  providedIn: 'root'
})
export class PredictionsRepository {
  constructor(private weatherService: WeatherService) {
  }

  getPredictionsForStation(station: Station, predictor: Predictor): Observable<Prediction[]> {
    return this.weatherService.getPredictions(station._id, predictor.name);
  }

  getMappedPredictions(station: Station, predictor: Predictor): Observable<PredictionData> {
    return this.getPredictionsForStation(station, predictor)
      .pipe(
        map(x => this.mapPredictionData(x))
      );
  }

  mapPredictionData(predictions: Prediction[]): PredictionData {
    const predictionDates = predictions.map(prediction => prediction.timestamp.getTime());

    const predictionsMap = {
      pm25: predictions.map(prediction => prediction.airQuality.pm25),
      pm10: predictions.map(prediction => prediction.airQuality.pm10),
      o3: predictions.map(prediction => prediction.airQuality.o3),
    };

    const result: any = {};
    for (const key in predictionsMap) {
      result[key] = predictionDates.map(function (e, ind) {
        return [e, predictionsMap[key][ind]];
      });
      result[key].sort();
    }

    return result;
  }
}
