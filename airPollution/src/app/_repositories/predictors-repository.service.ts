import {Injectable} from '@angular/core';
import {WeatherService} from '../_services/weather.service';
import {ReplaySubject} from 'rxjs/internal/ReplaySubject';
import {Predictor} from '../_models/predictors';
import {Observable} from 'rxjs/internal/Observable';

@Injectable({
  providedIn: 'root'
})
export class PredictorsRepositoryService {
  private readonly predictorsReplaySubject: ReplaySubject<Predictor[]>;
  private readonly predictorObservable: Observable<Predictor[]>;

  constructor(private weatherService: WeatherService) {
    this.predictorsReplaySubject = new ReplaySubject<Predictor[]>(1);
    this.predictorObservable = this.predictorsReplaySubject.asObservable();

    this.weatherService.getPredictors()
      .subscribe(predictors => this.predictorsReplaySubject.next(predictors));
  }

  public getAll(): Observable<Predictor[]> {
    return this.predictorObservable;
  }
}
