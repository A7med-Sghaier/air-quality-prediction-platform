import { AfterViewChecked, Directive, ElementRef, Input } from '@angular/core';
import { chart } from 'highcharts';
import * as Highcharts from 'highcharts';
import { darkTheme } from '../_themes/highchartDarkTheme';
import { ErrorMetric } from '../_models/ErrorMetric';

export interface PredictorSeriesEntry {
  pointPlacement?: string;
  type?: string;
  name: string;
  data: number[];
}

@Directive({
  selector: '[appPredictorsComparisonBcByPred]'
})
export class PredictorsComparisonBcByPredDirective implements AfterViewChecked {
  private chart?: Highcharts.ChartObject;
  private _seriesEntries: PredictorSeriesEntry[] = [];
  private _categories: string[] = [];

  @Input('errorMetric') errorMetric: ErrorMetric;

  @Input('seriesEntries') set seriesEntries(entries: PredictorSeriesEntry[]) {
    this._seriesEntries = entries;
    if (this._categories.length > 0 && this._seriesEntries.length > 0) {
      this.initializeChart();
    }
  }

  @Input('categories') set categories(categories: string[]) {
    this._categories = categories;
    if (this._categories.length > 0 && this._seriesEntries.length > 0) {
      this.initializeChart();
    }
  }

  constructor(private elemRef: ElementRef) {
  }

  private initializeChart() {
    Highcharts.setOptions(darkTheme);
    const options: Highcharts.Options = {
      chart: {
        type: 'column'
      },
      title: {
        text: 'Grouped by predictor'
      },
      xAxis: {
        categories: this._categories,
        crosshair: true
      },
      yAxis: {
        min: 0,
        title: {
          text: this.errorMetric.name,
        }
      },
      tooltip: {
        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
        '<td style="padding:0"><b>{point.y:.1f}</b></td></tr>',
        footerFormat: '</table>',
        shared: true,
        useHTML: true
      },
      plotOptions: {
        column: {
          pointPadding: 0.2,
          borderWidth: 0
        }
      },
      series: this._seriesEntries,
    };

    this.chart = chart(this.elemRef.nativeElement, options);
  }

  ngAfterViewChecked(): void {
    if (this.chart === undefined) {
      return;
    }
    this.chart.reflow();
  }
}
