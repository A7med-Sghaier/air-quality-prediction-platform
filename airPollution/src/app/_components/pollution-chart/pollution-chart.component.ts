import {Component, OnInit, QueryList, ViewChildren} from '@angular/core';
import {Chart} from 'chart.js';
import {StationPublisherService} from '../../_services/station-publisher.service';
import {Predictor} from '../../_models/predictors';
import {Station} from '../../_models/Station';
import {AirPollutionData, AirPollutionRepositoryService} from '../../_repositories/air-pollution-repository.service';
import {PredictorsRepositoryService} from '../../_repositories/predictors-repository.service';
import {PollutionChartDirective} from '../../_directives/pollution-chart.directive';
import {PollutionAttribute, PollutionAttributes} from '../../_models/AirPollution';
import {PredictionData, PredictionsRepository} from '../../_repositories/prediction-repository.service';
import {FormControl} from '@angular/forms';
import {PredictorSeriesEntry} from '../../_directives/predictors-comparison-bc-by-pred.directive';
import {ErrorMetric} from '../../_models/ErrorMetric';

@Component({
  selector: 'app-pollution-chart',
  templateUrl: './pollution-chart.component.html',
  styleUrls: ['./pollution-chart.component.scss']
})
export class PollutionChartComponent implements OnInit {
  private chartAttrMapping: Map<PollutionAttribute, PollutionChartDirective> = new Map<PollutionAttribute, PollutionChartDirective>();
  private pollutionData: AirPollutionData;
  private _visiblePredictors: Set<string>;

  @ViewChildren(PollutionChartDirective) set content(content: QueryList<PollutionChartDirective>) {
    this.chartAttrMapping.clear();
    content.forEach(directive => {
      this.chartAttrMapping.set(directive.pollutionAttr, directive);
    });
  }
  pollutionAttr = PollutionAttributes;
  station: Station | null = null;
  predictors: Predictor[] = [];
  predictions: Map<string, PredictionData>;
  visiblePredictions: Set<PollutionAttribute>;
  visiblePredictors: Set<string>;
  visiblePredictorsControl = new FormControl();


  showPredictors = false;

  constructor(
    private airPollutionRepository: AirPollutionRepositoryService,
    private stationPublisher: StationPublisherService,
    private predictionRepository: PredictionsRepository,
    private predictorsRepository: PredictorsRepositoryService
  ) {
    this.predictions = new Map<string, PredictionData>();
    this.visiblePredictions = new Set<PollutionAttribute>();
    this.visiblePredictors = new Set<string>();
  }

  public isPredictorEnabled(predictor: Predictor): boolean {
    return this.visiblePredictors.has(predictor.name);
  }

  public isPredictionEnabled(pollutionAttribute: PollutionAttribute): boolean {
    return this.visiblePredictions.has(pollutionAttribute);
  }

  async showPredictor(predictor: Predictor) {
    await this.loadPredictor(predictor);
    if (this.visiblePredictors.has(predictor.name)) {
      this.visiblePredictors.delete(predictor.name);
    } else {
      this.visiblePredictors.add(predictor.name);
    }

    this.renderAll();
  }

  private async loadPredictor(predictor: Predictor): Promise<void> {
    if (this.predictions.has(predictor.name)) {
      return;
    }

    return new Promise<void>((resolve) => {
      this.predictionRepository.getMappedPredictions(this.station, predictor)
        .subscribe((predictions) => {
          this.predictions.set(predictor.name, predictions);
          resolve();
        });
    });
  }

  showPredictionMetric(pollutionAttribute: PollutionAttribute) {
    if (this.visiblePredictions.has(pollutionAttribute)) {
      this.visiblePredictions.delete(pollutionAttribute);
    } else {
      this.visiblePredictions.add(pollutionAttribute);
    }

    this.rerenderAttribute(pollutionAttribute);
  }

  private renderAll() {
    for (const attr of this.pollutionAttr) {
      this.rerenderAttribute(attr);
    }
  }

  private rerenderAttribute(pollutionAttribute: PollutionAttribute) {
    const chart = this.chartAttrMapping.get(pollutionAttribute).chart;
    while (chart.series.length > 0) {
      chart.series[0].remove(true);
    }

    this.showData(pollutionAttribute);
    this.renderPredictionsForAttribute(pollutionAttribute);
  }

  private renderPredictionsForAttribute(pollutionAttribute: PollutionAttribute) {
    if (!this.visiblePredictions.has(pollutionAttribute)) {
      return;
    }

    for (const name of Array.from(this.visiblePredictors.values())) {
      this.chartAttrMapping.get(pollutionAttribute).chart.addSeries({
        name: name,
        data: this.getDataForAttribute(this.predictions.get(name), pollutionAttribute)
      });
    }
  }

  private getDataForAttribute(predictionData: PredictionData, attribute: PollutionAttribute): any {
    switch (attribute) {
      case PollutionAttribute.O3:
        return predictionData.o3;
      case PollutionAttribute.CO:
        return predictionData.pm10;
      case PollutionAttribute.PM25:
        return predictionData.pm25;
    }
  }

  ngOnInit() {
    this.stationPublisher.getStationObservable()
      .subscribe(station => {
        this.station = station;
        if (this.station === null || !this.station.isAqStation()) {
          return;
        }

        this.updatePollution(station);
      });
    this.predictorsRepository.getAll()
      .subscribe(predictors => this.predictors = predictors);

    this.visiblePredictorsControl.valueChanges.subscribe(val => {
      this.visiblePredictors = new Set<string>(val);
    });
  }

  private showData(attribute: PollutionAttribute) {
    if (!this.chartAttrMapping.has(attribute)) {
      return;
    }

    let p: number[] = [];
    switch (attribute) {
      case PollutionAttribute.SO2:
        p = this.pollutionData.so2;
        break;
      case PollutionAttribute.NO2:
        p = this.pollutionData.no2;
        break;
      case PollutionAttribute.PM10:
        p = this.pollutionData.pm10;
        break;
      case PollutionAttribute.PM25:
        p = this.pollutionData.pm25;
        break;
      case PollutionAttribute.CO:
        p = this.pollutionData.co;
        break;
      case PollutionAttribute.O3:
        p = this.pollutionData.o3;
        break;
      default:
        throw new Error('sdlfkj');
    }

    const data: any = this.pollutionData.airPollutionDates.map(function (e, i) {
      return [e, p[i]];
    });

    this.chartAttrMapping.get(attribute).chart.addSeries({
      name: 'Actual data',
      type: 'area',
      data: data
    });
  }

  private updatePollution(station: Station): void {
    this.pollutionData = this.airPollutionRepository.createAirPollutionDataObject();
    this.airPollutionRepository.getTimeMappedAirPollutionData(station)
      .subscribe(airPollutionData => {
        this.pollutionData = airPollutionData;
        for (const attr of PollutionAttributes) {
          this.showData(attr);
        }
      });
  }

  updatePredictors() {

  }
}
