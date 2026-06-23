import {Directive, ElementRef, Input} from '@angular/core';
import {WeatherAttribute} from '../_models/Weather';
import {chart} from 'highcharts';
import * as Highcharts from 'highcharts';

@Directive({
  selector: '[appWeatherChart]'
})
export class WeatherChartDirective {
  private attr?: WeatherAttribute;
  public chart: Highcharts.ChartObject;

  constructor(private elemRef: ElementRef) {
  }

  @Input('weatherAttr') set weatherAttr(val: WeatherAttribute) {
    this.attr = val;
    if (this.attr !== undefined) {
      this.initializeChart();
    }
  }

  get weatherAttr(): WeatherAttribute | undefined {
    return this.attr;
  }

  initializeChart() {
    const options: Highcharts.Options = {
      colors: ['#007bff', '#6610f2', '#ee5f5b', '#f89406', '#62c462', '#62c462',
        '#eeaaee', '#55BF3B', '#DF5353', '#7798BF', '#aaeeee'],
      chart: {
        backgroundColor: 'rgba(255,255,255,0)',
        style: {
          fontFamily: '\'Unica One\', sans-serif'
        },
        plotBorderColor: '#606063',
        zoomType: 'x'
      },
      title: {
        text: this.attr.toString(),
        style: {
          color: '#7A8288',
        }
      },
      xAxis: {
        type: 'datetime',
      },
      yAxis: {
        title: {
          text: this.attr.toString()
        }
      },
      legend: {
        enabled: false
      },

      series: [{
        type: 'area',
        name: 'Actual data',
        data: []
      }]
    };
    this.chart = chart(this.elemRef.nativeElement, options);
  }
}
