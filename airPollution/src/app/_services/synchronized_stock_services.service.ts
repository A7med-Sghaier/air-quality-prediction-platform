/*************************************************************
 * airPollution - synchronized_stock_services.service.ts
 *
 * created by : Ahmed Sghaier - a7mado008@gmail.com
 * created on : 06.07.18 - 12:39
 * version : 1.0
 * copyright : all right reserved 2018
 *************************************************************/

import { Injectable } from '@angular/core';
import * as HighStock from 'highcharts/highstock';

@Injectable()
export class SynchronizedStockService {
  series = [];
  yAxis = [];
  predictorsSeries = [];
  attributesIndices = [];
  predictorsColors = {
    'fcnn': '#ffcc22',
    'mean': '#fff',
    'cnn': '#ab7445',
    'gradientboost': '#ba209d',
    'adaboost': '#ab9c30',
    'regression_forest': '#99ab6f',
    'bagging': '#9c72ab',
    'linear_regression': '#ab9c30',
  };

  constructor() {
  }

  addSeries(dataset) {
    this.attributesIndices.push(dataset.name);
    this.series.push(dataset);
  }

  initChart() {
    this.series = [];
    this.yAxis = [];
    this.predictorsSeries = [];
    this.attributesIndices = [];
  }

  initPredictionsSeries(predictions) {
    this.predictorsSeries = [];
    predictions.forEach((predictor, predictorKey) => {
      for (const attrKey in predictor) {
        const series = this.series.find(item => item.id === attrKey);
        if (series === undefined) {
          return;
        }
        const attributData = predictor[attrKey];
        const dataset = {
          data: attributData,
          id: predictorKey + attrKey,
          name: attrKey + '(' + predictorKey + ')',
          type: 'line',
          color: this.predictorsColors[predictorKey],
          tooltip: {
            valueDecimals: 1,
            valueSuffix: ' µg/m3'
          },
          threshold: 2,
          yAxis: this.attributesIndices.indexOf(attrKey)
        };
        this.predictorsSeries.push(dataset);
      }
    });
    console.log('2---- ', [...this.series, ...this.predictorsSeries]);

  }

  initYAxis() {
    for (let i = 0; i < this.series.length; i++) {
      this.yAxis.push(
        {
          labels: {
            align: 'right',
            x: -5
          },
          title: {
            x: 5,
            text: this.series[i].name,
            style: {
              fontSize: '16px',
              fontWeight: '650',
              paddingLeft: '15px',
              color: HighStock.getOptions().colors[i],
            }
          },
          top: (i * (100 / this.series.length)) + '%',
          // top: ((i * 110) + 150) + 'px',
          height: '100px',
          offset: 0,
          lineWidth: 2,
          style: {
            backgroundColor: '#fff',

          },
          resize: {
            enabled: true
          }
        });
    }
  }

  renderSynchStockChart(): any {
    return {
      chart: {
        // marginLeft: 5, // Keep all charts left aligned
        spacingTop: 20,
        spacingBottom: 20,
        maxWidth: '520px',
        height: (this.series.length * 170),
      },
      tooltip: {
        shared: true
      },
      rangeSelector: {

        buttons: [{
          type: 'day',
          count: 1,
          text: '1d'
        }, {
          type: 'day',
          count: 3,
          text: '3d'
        }, {
          type: 'week',
          count: 1,
          text: '1w'
        }, {
          type: 'month',
          count: 1,
          text: '1m'
        }, {
          type: 'month',
          count: 2,
          text: '2m'
        }, {
          type: 'month',
          count: 3,
          text: '3m'
        }, {
          type: 'month',
          count: 6,
          text: '6m'
        }, {
          type: 'year',
          count: 1,
          text: '1y'
        }, {
          type: 'all',
          text: 'All'
        }],
        inputEnabled: true, // it supports only days
        selected: 3
      },

      title: {
        text: 'Air Quality'
      },

      subtitle: {
        text: 'Historical'
      },

      xAxis: {
        //minRange: 3600 * 1000 // one hour
      },

      yAxis: this.yAxis,

      plotOptions: {
        series: {
          dataGrouping: {
            units: groupingUnits
          }
        },
        area: {
          shadow: true
        }
      },

      series: [...this.series, ...this.predictorsSeries]
    };
  }
}

// set the allowed units for data grouping
const groupingUnits = [
  ['hour', [1, 2, 3, 4, 6, 8, 12, 24]],
  ['day', [1, 2, 3, 4, 6]],
  ['week', [1]],
  ['month', [1, 2, 3, 4, 6]]
];
