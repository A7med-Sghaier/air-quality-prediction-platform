import { AfterViewChecked, AfterViewInit, Directive, ElementRef, Input } from '@angular/core';
import { chart } from 'highcharts';
import * as Highcharts from 'highcharts';
import { PredictorSeriesEntry } from './predictors-comparison-bc-by-pred.directive';
import { darkTheme } from '../_themes/highchartDarkTheme';
import { ErrorMetric } from '../_models/ErrorMetric';

@Directive({
  selector: '[appPredictorsComparison]'
})
export class PredictorsComparisonDirective implements AfterViewChecked {
  private chart?: Highcharts.ChartObject;
  private _seriesEntries: PredictorSeriesEntry[] = [];

  @Input('errorMetric') errorMetric: ErrorMetric;

  @Input('seriesEntries') set seriesEntries(entries: PredictorSeriesEntry[]) {
    for (const entry of entries) {
      entry.type = 'column';
    }
    this._seriesEntries = entries;
    if (entries.length > 0) {
      this.initializeChart();
    }
  }

  constructor(private elemRef: ElementRef) {
  }

  private initializeChart() {
    Highcharts.setOptions(darkTheme);
    const options = {
      chart: {
        type: 'column'
      },
      title: {
        text: 'Group by pollution attribute'
      },
      xAxis: {
        categories: ['PM25', 'PM10', 'O3'],
        crosshair: true
      },
      yAxis: {
        min: 0,
        title: {
          text: this.errorMetric.name
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
