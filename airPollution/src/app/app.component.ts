import { Component, OnInit } from '@angular/core';
import { Chart } from 'chart.js';

import { WeatherService } from './_services/weather.service';
import { footerVals } from './_models/footer';
import { CITIES, City } from './_models/City';
import { CityPublisherService } from './_services/city-publisher.service';
import { StationPublisherService } from './_services/station-publisher.service';
import { Station } from './_models/Station';
import { setTheme } from 'ngx-bootstrap';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  station: Station | null = null;
  cities = CITIES;
  currentCity: City;
  footer = footerVals;

  constructor(
    private _weather: WeatherService,
    private cityPublisher: CityPublisherService,
    private stationPublisher: StationPublisherService
  ) {
    setTheme('bs3');
  }

  ngOnInit() {
    this.changeCity(this.cities[1]);
    this.stationPublisher.getStationObservable()
      .subscribe(station => this.station = station);
  }

  changeCity(city: City) {
    this.currentCity = city;
    this.cityPublisher.publishCity(city);
  }

  closeOverlay(): void {
    this.stationPublisher.publishStation(null);
  }
}
