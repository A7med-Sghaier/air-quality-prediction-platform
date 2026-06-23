import {Component, OnInit} from '@angular/core';
import {CityPublisherService} from '../../_services/city-publisher.service';
import {City} from '../../_models/City';
import {WeatherService} from '../../_services/weather.service';
import {Station} from '../../_models/Station';
import {StationPublisherService} from '../../_services/station-publisher.service';

@Component({
  selector: 'app-stations-map',
  templateUrl: './stations-map.component.html',
  styleUrls: ['./stations-map.component.css']
})
export class StationsMapComponent implements OnInit {
  readonly gridIcon = 'assets/grid.png';
  readonly stationIcon = 'assets/station.png';
  readonly selectedStationIcon = 'assets/blue_MarkerA.png';
  readonly aqStationsIcon = 'assets/darkgreen_MarkerA.png';

  city: City | null = null;
  stations: Station[] = [];
  selectedStation: Station | null = null;

  showAqStations = true;
  showWeatherStations = true;
  showGridStations = false;

  constructor(
    private cityPublisher: CityPublisherService,
    private weatherService: WeatherService,
    private stationPublisher: StationPublisherService
  ) {
  }

  getIcon(station: Station) {
    if (this.selectedStation !== null && station._id === this.selectedStation._id) {
      return this.selectedStationIcon;
    }

    if (station.is_grid) {
      return this.gridIcon;
    }

    if (station.isAqStation()) {
      return this.aqStationsIcon;
    }

    return this.stationIcon;
  }

  ngOnInit() {
    this.cityPublisher.getCityObservable()
      .subscribe(city => {
        console.log(city);
        this.city = city;
        this.weatherService.getStationsForCity(city)
          .subscribe(stations => this.stations = stations);
      });
  }

  publishStation(station: Station) {
    this.selectedStation = station;
    this.stationPublisher.publishStation(station);
  }

  showStation(station: Station): boolean {
    if (station.is_grid) {
      return this.showGridStations;
    } else if (station.isAqStation()) {
      return this.showAqStations;
    }

    return this.showWeatherStations;
  }
}
