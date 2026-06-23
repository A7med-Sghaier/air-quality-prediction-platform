import { AfterViewChecked, Directive, ElementRef, Input } from '@angular/core';
import { chart } from 'highcharts';
import * as Highcharts from 'highcharts';
import { PredictorSeriesEntry } from './predictors-comparison-bc-by-pred.directive';
import { darkTheme } from '../_themes/highchartDarkTheme';

require('highcharts/highcharts-more')(Highcharts);

@Directive({
  selector: '[appPredictorsComparisonSpiderweb]'
})
export class PredictorsComparisonSpiderwebDirective implements AfterViewChecked {
  private chart?: Highcharts.ChartObject;
  private _seriesEntries: PredictorSeriesEntry[] = [];

  @Input('seriesEntries') set seriesEntries(entries: PredictorSeriesEntry[]) {
    for (const entry of entries) {
      entry.pointPlacement = 'on';
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
    const options: any = {

      chart: {
        polar: true,
        type: 'line'
      },

      title: {
        text: '',
        x: -80
      },

      pane: {
        size: '80%'
      },

      xAxis: {
        // categories: ['Sales', 'Marketing', 'Development', 'Customer Support',
        //   'Information Technology', 'Administration'],
        categories: ['PM25', 'PM10', 'O3'],
        tickmarkPlacement: 'on',
        lineWidth: 0
      },

      yAxis: {
        gridLineInterpolation: 'polygon',
        lineWidth: 0,
        min: 0
      },

      tooltip: {
        shared: true,
        pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:,.0f}</b><br/>'
      },

      legend: {
        align: 'right',
        verticalAlign: 'top',
        y: 70,
        layout: 'vertical'
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

