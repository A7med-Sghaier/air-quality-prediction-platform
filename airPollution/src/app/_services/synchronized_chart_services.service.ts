/*************************************************************
 * airPollution - synchronized_chart_services.service.ts
 *
 * created by : Ahmed Sghaier - a7mado008@gmail.com
 * created on : 03.07.18 - 21:25
 * version : 1.0
 * copyright : all right reserved 2018
 *************************************************************/
import {Injectable} from '@angular/core';

import * as _moment from 'moment';
const moment = _moment;

import * as Highcharts from 'highcharts';
import * as HighStock from 'highcharts/highstock';
import * as ChartsMore from 'highcharts-more';
ChartsMore(Highcharts);
ChartsMore(HighStock);


@Injectable()
export class SynchronizedChartService {
  dates = [];
  series;
  chart;
  constructor() {}

  /**
   * Highlight a point by showing tooltip, setting hover state and draw crosshair
   */
  highlight(point, event) {
    event = point.series.chart.pointer.normalize(event);
    point.onMouseOver(); // Show the hover marker
    point.series.chart.tooltip.refresh(point); // Show the tooltip
    point.series.chart.xAxis[0].drawCrosshair(event, point); // Show the crosshair
  }

  /**
   * Synchronize zooming through the setExtremes event handler.
   */
  syncExtremes(e) {
    if (e.trigger !== 'syncExtremes') { // Prevent feedback loop
      for (const chart of Highcharts.charts) {
        console.log('------', chart)
        if (chart !== this.chart) {
          if (chart.xAxis[0].setExtremes) {
            chart.xAxis[0].setExtremes(
              e.min,
              e.max,
              undefined,
              false,
              { trigger: 'syncExtremes' }
            );
          }
        }
      }
    }
  }

  renderSynchChart(dataset, index): any {
    return {
      chart: {
        marginLeft: 5, // Keep all charts left aligned
        spacingTop: 20,
        spacingBottom: 20,
        maxWidth: '520px'
      },
      title: {
        text: dataset.name,
        align: 'left',
        margin: 0,
        x: 30
      },
      credits: {
        enabled: false
      },
      legend: {
        enabled: false
      },
      xAxis:[{
        type: 'datetime',
        crosshair: true,
        events: {
          setExtremes: this.syncExtremes
        },
        labels: {
          format: '{value:%H}'
        }
      },
        { // Top X axis
          linkedTo: 0,
          type: 'datetime',
          tickInterval: 24 * 3600 * 1000,
          labels: {
            format: '{value:<span style="font-size: 12px; font-weight: bold">%a</span> %b %e}',
            align: 'left',
            x: 3,
            y: -5
          },
          opposite: true,
          tickLength: 20,
          gridLineWidth: 1
        }],
      yAxis: {
        title: {
          text: null
        }
      },
      tooltip: {
        positioner: function () {
          return {
            // right aligned
            x: this.chart.chartWidth - this.label.width,
            y: 10 // align to title
          };
        },
        borderWidth: 0,
        backgroundColor: 'none',
        pointFormat: '{point.y}',
        headerFormat: '',
        shadow: false,
        style: {
          fontSize: '18px'
        },
        valueDecimals: dataset.valueDecimals
      },
      series: [{
        data: dataset.data,
        name: dataset.name,
        type: dataset.type,
        color: Highcharts.getOptions().colors[index],
        fillOpacity: 0.3,
        tooltip: {
          valueSuffix: ' ' + dataset.unit
        }
      }]
    };
  }
}
