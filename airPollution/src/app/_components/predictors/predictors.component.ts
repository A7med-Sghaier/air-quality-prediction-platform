import { Component, OnInit } from '@angular/core';
import { PredictorsRepositoryService } from '../../_repositories/predictors-repository.service';
import { Predictor } from '../../_models/predictors';
import { PollutionAttribute } from '../../_models/AirPollution';
import { ErrorMetricRepositoryService } from '../../_repositories/error-metric-repository.service';
import { ErrorMetric, ErrorMetricValue } from '../../_models/ErrorMetric';
import { StationPublisherService } from '../../_services/station-publisher.service';
import { Station } from '../../_models/Station';
import { flatMap } from 'rxjs/operators';
import { FormControl } from '@angular/forms';
import { PredictorSeriesEntry } from '../../_directives/predictors-comparison-bc-by-pred.directive';


const percentColors = [
  {pct: 1.0, color: {r: 0x00, g: 0xff, b: 0}},
  {pct: 0.5, color: {r: 0xff, g: 0xff, b: 0}},
  {pct: 1.0, color: {r: 0xff, g: 0x00, b: 0}}
];

@Component({
  selector: 'app-predictors',
  templateUrl: './predictors.component.html',
  styleUrls: ['./predictors.component.scss']
})
export class PredictorsComponent implements OnInit {
  predictors: Predictor[] = [];
  errorMetrics: ErrorMetric[];

  public readonly visibleAttributes = [PollutionAttribute.PM25, PollutionAttribute.PM10, PollutionAttribute.O3];
  private _visiblePredictors: Set<string>;
  visiblePredictors: string[] = [];
  visiblePredictorsControl = new FormControl();

  visibleMetric: ErrorMetric | null;
  visibleMetricControl = new FormControl();
  private station: Station | null = null;
  private metricCache: Map<string, ErrorMetricValue[]>;

  series = [];
  swSeries = [];
  seriesByPred = [];

  constructor(
    private stationPublisher: StationPublisherService,
    private predictorsRepository: PredictorsRepositoryService,
    private errorMetricRepository: ErrorMetricRepositoryService
  ) {
    this._visiblePredictors = new Set<string>();
    this.metricCache = new Map<string, ErrorMetricValue[]>();
  }

  updateSeriesData() {
    this.visibleMetric = this.visibleMetricControl.value;

    const series: PredictorSeriesEntry[] = [];

    for (const predictor of Array.from(this.visiblePredictors.values())) {
      const entry: PredictorSeriesEntry = {
        name: predictor,
        data: [],
      };
      for (const attr of this.visibleAttributes) {
        const dataPoint = this.getMetricForPredictorAndAttribute(attr, predictor);
        entry.data.push(dataPoint);
      }

      series.push(entry);
    }

    this.series = JSON.parse(JSON.stringify(series));
    this.swSeries = JSON.parse(JSON.stringify(series));

    this.prepareSeriesByPred();
  }

  private prepareSeriesByPred() {
    const series: PredictorSeriesEntry[] = [];

    for (const attr of this.visibleAttributes) {
      const entry: PredictorSeriesEntry = {
        name: attr,
        data: [],
      };
      for (const predictor of this.visiblePredictors) {
        const dataPoint = this.getMetricForPredictorAndAttribute(attr, predictor);
        entry.data.push(dataPoint);
      }
      series.push(entry);
    }

    this.seriesByPred = series;
  }

  updatePredictors() {
    this._visiblePredictors = new Set<string>();
    for (const pred of this.visiblePredictorsControl.value) {
      this.addPredictor(pred);
    }
  }

  ngOnInit() {
    this.errorMetricRepository.getAll()
      .pipe(
        flatMap(errorMetrics => {
          this.errorMetrics = errorMetrics;
          this.visibleMetricControl.setValue(this.errorMetrics[0]);

          return this.predictorsRepository.getAll();
        }),
      )
      .subscribe(predictors => {
        this.predictors = predictors;
        this.visiblePredictorsControl.setValue(predictors);
        this.updatePredictors();
      });
    this.stationPublisher.getStationObservable()
      .subscribe(station => this.station = station);
  }

  getColorClassForPrediction(attribute: PollutionAttribute, predictor: string): string {
    const metric = this.getMetricForPredictorAndAttribute(attribute, predictor);
    const maxValue = this.getMaxValueForAttribute(attribute);

    const percentage = 100 / maxValue * metric / 100;
    return this.generateColor(percentage);
  }

  private addPredictor(predictor: Predictor) {
    this.errorMetricRepository.getMetricsByStation(predictor, this.station)
      .subscribe(metrics => {
        this._visiblePredictors.add(predictor.name);
        this.visiblePredictors = Array.from(this._visiblePredictors.values());
        this.metricCache.set(predictor.name, metrics);
        this.updateSeriesData();
      });
  }

  private generateColor(pct) {
    // https://stackoverflow.com/questions/7128675/from-green-to-red-color-depend-on-percentage
    let i: number;
    for (i = 1; i < percentColors.length - 1; i++) {
      if (pct < percentColors[i].pct) {
        break;
      }
    }
    const lower = percentColors[i - 1];
    const upper = percentColors[i];
    const range = upper.pct - lower.pct;
    const rangePct = (pct - lower.pct) / range;
    const pctLower = 1 - rangePct;
    const pctUpper = rangePct;
    const color = {
      r: Math.floor(lower.color.r * pctLower + upper.color.r * pctUpper),
      g: Math.floor(lower.color.g * pctLower + upper.color.g * pctUpper),
      b: Math.floor(lower.color.b * pctLower + upper.color.b * pctUpper)
    };
    return 'rgb(' + [color.r, color.g, color.b].join(',') + ')';
  }

  private getMaxValueForAttribute(attr: PollutionAttribute) {
    let max = 0;

    for (const predictor of this.visiblePredictors) {
      const val = this.getMetricForPredictorAndAttribute(attr, predictor);
      max = (max >= val) ? max : val;
    }

    return max;
  }

  getMetricForPredictorAndAttribute(attribute: PollutionAttribute, predictor: string): number {
    const metricValues = this.metricCache.get(predictor);
    if (metricValues === undefined) {
      return -1;
    }

    for (const metricValue of metricValues) {
      if (metricValue.type === this.visibleMetric.key) {
        switch (attribute) {
          case PollutionAttribute.PM25:
            return metricValue.airPollution.pm25;
          case PollutionAttribute.SO2:
            return metricValue.airPollution.so2;
          case PollutionAttribute.NO2:
            return metricValue.airPollution.no2;
          case PollutionAttribute.PM10:
            return metricValue.airPollution.pm10;
          case PollutionAttribute.CO:
            return metricValue.airPollution.co;
          case PollutionAttribute.O3:
            return metricValue.airPollution.o3;
        }
      }
    }

    return -1;
  }
}
