import {Component, Input, OnInit, AfterViewInit, ViewChild, ElementRef, TemplateRef, OnDestroy, OnChanges} from '@angular/core';
import {AirPollutionRepositoryService} from '../../_repositories/air-pollution-repository.service';
import {Station} from '../../_models/Station';
import { chart } from 'highcharts';
import {SynchronizedChartService} from '../../_services/synchronized_chart_services.service';
import * as Highcharts from 'highcharts';
import {darkTheme} from '../../_themes/highchartDarkTheme';
import * as ChartsMore from 'highcharts-more';
import * as HighStock from 'highcharts/highstock';
import {SynchronizedStockService} from '../../_services/synchronized_stock_services.service';
import {Predictor} from '../../_models/predictors';
import {PredictionData, PredictionsRepository} from '../../_repositories/prediction-repository.service';
import {takeWhile} from 'rxjs/operators';
import {BehaviorSubject} from 'rxjs';
ChartsMore(Highcharts);
ChartsMore(HighStock);

@Component({
  selector: 'app-synchronized-chart',
  templateUrl: './synchronized-chart.component.html',
  styleUrls: ['./synchronized-chart.component.css']
})
export class SynchronizedChartComponent implements OnInit, AfterViewInit, OnDestroy, OnChanges {

  @Input() pollutionAttributs;
  @Input() station: Station;
  @Input() visiblePredictors;
  @ViewChild('synchronizedchart') chartTarget: ElementRef;
  chart;
  dates;
  pollutionData;
  predictions: Map<string, PredictionData>;
  wait = true;

  constructor(private airPollutionRepository: AirPollutionRepositoryService,
              private synchChartSrvc: SynchronizedChartService,
              private predictionRepository: PredictionsRepository,
              private synchChartSrvc2: SynchronizedStockService) {
    this.predictions = new Map<string, PredictionData>();
  }

  ngOnInit() {
    // this.initSynchronisedChartObject()
    this.airPollutionRepository.getTimeMappedAirPollutionData(this.station)
      .subscribe(airPollutionData => {
        this.pollutionData = airPollutionData;
        this.dates = airPollutionData.airPollutionDates;
        this.initSynchronisedStockChartObject();
      });
  }

  ngOnChanges(changes) {
    if (changes.visiblePredictors) {
      this.loadPredictors(changes.visiblePredictors.currentValue);
    }
  }

  loadPredictors(pridictors) {
    this.predictions = new Map<string, PredictionData>();

    if (pridictors.size <= 0) {
      this.redrawChart();
      this.chart = HighStock.stockChart(this.chartTarget.nativeElement , this.synchChartSrvc2.renderSynchStockChart());
    }

    pridictors.forEach(predictor => {
      this.loadPredictor(predictor);
    });
  }

   private async loadPredictor(predictor: Predictor): Promise<void> {
    return new Promise<void>((resolve) => {
      this.predictionRepository.getMappedPredictions(this.station, predictor)
        .subscribe((predictions) => {
          this.predictions.set(predictor.name, predictions);
          if (this.predictions.size === this.visiblePredictors.size) {
            this.redrawChart();
            this.chart = HighStock.stockChart(this.chartTarget.nativeElement , this.synchChartSrvc2.renderSynchStockChart());
          }
          resolve();
        });
    });
  }

  ngOnDestroy() {
    const len = Highcharts.charts.length;
    for (let i = 0; i < len; i++) {
      Highcharts.charts.pop();
    }
  }

  ngAfterViewInit() {}

  initSynchronisedChartObject() {
    Highcharts.setOptions(darkTheme);
    this.pollutionAttributs.forEach((attribut, i) => {
      const dataset = {
        data: this.pollutionData[attribut].map((val, j) => [this.dates[j], val]),
        name: attribut,
        unit: 'ug/x',
        type: 'line',
        valueDecimals: 1
      };
      const e = document.createElement('div')
      e.setAttribute('class', 'col-12')
      chart(e , this.synchChartSrvc.renderSynchChart(dataset, i))
      this.chartTarget.nativeElement.appendChild(e);
    });
  }

  redrawChart() {
    this.synchChartSrvc2.initPredictionsSeries(this.predictions);
  }

  initSynchronisedStockChartObject() {
    HighStock.setOptions(darkTheme);
    this.synchChartSrvc2.initChart();

    let counter = 0;
    this.pollutionAttributs.forEach((attribut, i) => {
      if (this.pollutionData[attribut].filter(item => item != null).length > 0) {
        const dataset = {
          data: this.pollutionData[attribut].map((val, j) => [this.dates[j], val]),
          id: attribut,
          name: attribut,
          type: 'line',
          tooltip: {
            valueDecimals: 1,
            valueSuffix: ' µg/m3'
          },
          threshold: 2,
          yAxis: counter++
        };
        this.synchChartSrvc2.addSeries(dataset);
      }
    });

    this.synchChartSrvc2.initYAxis();
    this.chart = HighStock.stockChart(this.chartTarget.nativeElement , this.synchChartSrvc2.renderSynchStockChart());
  }

  synchTooltips(event) {
    let currentChart;
    let point;
    let e;
    for (let i = 0; i < Highcharts.charts.length; i++) {
      currentChart = Highcharts.charts[i];
      // Find coordinates within the chart
      e = currentChart.pointer.normalize(event);
      // Get the hovered point
      point = currentChart.series[0].searchPoint(e, true);
      if (point) {
        this.synchChartSrvc.highlight(point, event);
      }
    }
  }
}
