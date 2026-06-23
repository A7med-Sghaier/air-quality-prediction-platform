import {Injectable} from '@angular/core';
import {ReplaySubject} from 'rxjs/internal/ReplaySubject';
import {City} from '../_models/City';
import {Observable} from 'rxjs/internal/Observable';

@Injectable({
  providedIn: 'root'
})
export class CityPublisherService {
  private readonly cityReplaySubject: ReplaySubject<City>;
  private readonly cityObservable: Observable<City>;

  constructor() {
    this.cityReplaySubject = new ReplaySubject<City>(1);
    this.cityObservable = this.cityReplaySubject.asObservable();
  }

  public getCityObservable(): Observable<City> {
    return this.cityObservable;
  }

  public publishCity(city: City): void {
    this.cityReplaySubject.next(city);
  }
}
