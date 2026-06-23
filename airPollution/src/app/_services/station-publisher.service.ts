import {Injectable} from '@angular/core';
import {ReplaySubject} from 'rxjs/internal/ReplaySubject';
import {Station} from '../_models/Station';
import {Observable} from 'rxjs/internal/Observable';

@Injectable({
  providedIn: 'root'
})
export class StationPublisherService {
  private readonly stationReplaySubject: ReplaySubject<Station>;
  private readonly stationObservable: Observable<Station>;

  constructor() {
    this.stationReplaySubject = new ReplaySubject<Station>(1);
    this.stationObservable = this.stationReplaySubject.asObservable();
  }

  public getStationObservable(): Observable<Station> {
    return this.stationObservable;
  }

  public publishStation(station: Station): void {
    this.stationReplaySubject.next(station);
  }
}
