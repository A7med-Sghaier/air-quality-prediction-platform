import {Component, OnInit, QueryList, ViewChildren} from '@angular/core';
import {WeatherAttribute, WeatherAttributes, WeatherData} from '../../_models/Weather';
import {StationPublisherService} from '../../_services/station-publisher.service';
import {Station} from '../../_models/Station';
import {Chart} from 'chart.js';
import {PredictionsRepository} from '../../_repositories/prediction-repository.service';
import {WeatherRepositoryService} from '../../_repositories/weather-repository.service';
import {WeatherChartDirective} from '../../_directives/weather-chart.directive';
import {BehaviorSubject} from 'rxjs';

@Component({
  selector: 'app-weather-chart',
  templateUrl: './weather-chart.component.html',
  styleUrls: ['./weather-chart.component.css']
})

export class WeatherChartComponent implements OnInit {
  private chartAttrMapping: Map<WeatherAttribute, WeatherChartDirective> = new Map<WeatherAttribute, WeatherChartDirective>();
  private weatherData: WeatherData;
  private meteoData$: BehaviorSubject<WeatherData> = new BehaviorSubject<WeatherData>(new WeatherData());

  @ViewChildren(WeatherChartDirective) set content(content: QueryList<WeatherChartDirective>) {
    this.chartAttrMapping.clear();
    content.forEach(chart => {
      this.chartAttrMapping.set(chart.weatherAttr, chart);
    });
  }

  readonly weatherAttrDisplay: Map<WeatherAttribute, boolean>;
  readonly weatherAttr = WeatherAttributes;
  station: Station | null = null;

  constructor(
    private stationPublisher: StationPublisherService,
    private weatherRepository: WeatherRepositoryService
  ) {
    this.weatherAttrDisplay = new Map<WeatherAttribute, boolean>();
    for (const attr of WeatherAttributes) {
      this.weatherAttrDisplay.set(attr, false);
    }
  }

  ngOnInit() {
    // this.weatherData = new WeatherData();
    this.stationPublisher.getStationObservable()
      .subscribe(station => {
        this.station = station;

        if (this.station === null || this.station.isAqStation()) {
          return;
        }

        this.updateWeather(station);
      });
  }

  private showData(attribute: WeatherAttribute) {
    if (!this.chartAttrMapping.has(attribute)) {
      return;
    }

    let p: number[] = [];
    switch (attribute) {
      case WeatherAttribute.TEMPERATURE:
        p = this.weatherData.temperature;
        break;
      case WeatherAttribute.HUMIDITY:
        p = this.weatherData.humidity;
        break;
      case WeatherAttribute.PRESSURE:
        p = this.weatherData.pressure;
        break;
      case WeatherAttribute.WIND_SPEED:
        p = this.weatherData.wind;
        break;
      default:
        throw new Error('sdlfkj');
    }

    const data: any = this.weatherData.weatherDates.map(function (e, i) {
      return [e, p[i]];
    });

    this.chartAttrMapping.get(attribute).chart.series[0].remove(true);
    this.chartAttrMapping.get(attribute).chart.addSeries({
      name: 'Actual data',
      type: 'area',
      data: data
    });
  }

  updateWeather(station: Station) {
    this.weatherRepository.getMappedWeatherHistory(station)
      .subscribe(weatherData => {
        this.weatherData = new WeatherData(weatherData);
        this.meteoData$.next(this.weatherData)
        for (const attr of WeatherAttributes) {
          this.showData(attr);
        }
      });
  }

  get meteoData(): WeatherData {
    return this.meteoData$.getValue();
  }
}

