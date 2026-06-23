import {AfterViewInit, Component, ElementRef, Input, OnChanges, OnDestroy, OnInit, SimpleChanges, ViewChild} from '@angular/core';
import { chart } from 'highcharts';
import * as Highcharts from 'highcharts';
import * as ChartModuleMore from 'highcharts-more';
ChartModuleMore(Highcharts);
import {HightChartMeteoServices} from '../../_services/hight_chart_meteo_services.service';
import {WeatherData} from '../../_models/Weather';
import * as _moment from 'moment';
const moment = _moment;

@Component({
  selector: 'app-meteogram',
  templateUrl: './meteogram.component.html',
  styleUrls: ['./meteogram.component.css']
})
export class MeteogramComponent implements OnInit, AfterViewInit, OnChanges, OnDestroy {

  chart: Highcharts.ChartObject;
  @Input() meteoData: WeatherData;
  @Input() station;
  @ViewChild('meteogram') chartTarget: ElementRef;

  constructor(private highCahrtsSrvc: HightChartMeteoServices) { }

  ngOnInit() {
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.meteoData) {
      this.meteoData.setHumidity(changes.meteoData.currentValue.humidity);
      this.meteoData.setPressure(changes.meteoData.currentValue.pressure);
      this.meteoData.setTemperature(changes.meteoData.currentValue.temperature);
      this.meteoData.setWeatherDates(changes.meteoData.currentValue.weatherDates);
      this.meteoData.setWind(changes.meteoData.currentValue.wind);
      this.meteoData.setWindDirections(changes.meteoData.currentValue.windDirections);
      this.meteoData.setWeather(changes.meteoData.currentValue.weather);
      this.initializeChart();
    }
  }

  ngAfterViewInit() {
    this.initializeChart();
  }

  ngOnDestroy() {
    this.highCahrtsSrvc.destroyChart();
  }

  initializeChart() {
    if (!this.meteoData.isEmpty()) {
      this.highCahrtsSrvc.initData(this.chartTarget.nativeElement, this.meteoData, this.station);
    }
  }
}
