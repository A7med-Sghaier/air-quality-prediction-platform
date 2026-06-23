/*************************************************************
 * airPollution - hight_chart_meteo_services.service.ts
 *
 * created by : Ahmed Sghaier - a7mado008@gmail.com
 * created on : 30.06.18 - 15:15
 * version : 1.0
 * copyright : all right reserved 2018
 *************************************************************/
import { Injectable } from '@angular/core';
import { WeatherData } from '../_models/Weather';
import * as moment from 'moment';
import * as Highcharts from 'highcharts';
import * as HighStock from 'highcharts/highstock';
import * as ChartsMore from 'highcharts-more';
import * as ChartWindBard from 'highcharts/modules/windbarb';
import { darkTheme } from '../_themes/highchartDarkTheme';

ChartsMore(Highcharts);
ChartsMore(HighStock);
ChartWindBard(Highcharts);
ChartWindBard(HighStock);

/**
 import * as ChartSolidgauge from 'highcharts/modules/solid-gauge';
 ChartSolidgauge(Highcharts);
 **/

@Injectable({
  providedIn: 'root'
})
export class HightChartMeteoServices {
  symbols = [];
  dates = [];
  precipitations = [];
  precipitationsError = [];
  winds = [];
  temperatures = [];
  pressures = [];
  resolution: number;
  // Initialize
  station;
  city;
  container;
  chart;

  constructor() {
  }

  initData(container, data: WeatherData, station?, city?) {
    this.station = station || {};
    this.initChart();
    this.container = container;
    let pointStart: number;

    if (data.isEmpty()) {
      return this.error();
    }
    data.getWeatherDates().forEach((date, i) => {
      const from = date;
      const to = moment(date).add(1, 'hours').valueOf();

      // If it is more than an hour between points, show all symbols
      if (i === 0) {
        this.resolution = to - from;
      }

      this.dates.push(from);
      this.symbols.push(data.getWeather()[i]);

      this.temperatures.push({
        x: from,
        y: data.getTemperature()[i],
        to: to,
        symbolName: 'Partly cloudy'
      });

      if (i % 2 === 0) {
        this.winds.push({
          x: from,
          value: data.getWind()[i],
          direction: data.getWindDirections()[i]
        });
      }

      this.pressures.push({
        x: from,
        y: data.getPressure()[i]
      });

      if (i === 0) {
        pointStart = (from + to) / 2;
      }
    });

    // Smooth the line
    this.smoothLine(this.temperatures);

    // Create the chart when the data is loaded
    this.createChart();
  }

  /** ------------------ **/

  renderMeteoGram(): any {
    return {
      chart: {
        renderTo: this.container,
        // zoomType: 'x',
        marginBottom: 70,
        marginRight: 40,
        marginTop: 50,
        plotBorderWidth: 1,
        height: 450,
        alignTicks: false,
        scrollablePlotArea: {
          minWidth: 720
        }
      },
      rangeSelector: {

        buttons: [{
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
          count: 6,
          text: '6m'
        }, {
          type: 'year',
          count: 1,
          text: '1y'
        }],
        selected: 0
      },
      defs: {
        patterns: [{
          'id': 'precipitation-error',
          'path': {
            d: [
              'M', 3.3, 0, 'L', -6.7, 10,
              'M', 6.7, 0, 'L', -3.3, 10,
              'M', 10, 0, 'L', 0, 10,
              'M', 13.3, 0, 'L', 3.3, 10,
              'M', 16.7, 0, 'L', 6.7, 10
            ].join(' '),
            stroke: '#68CFE8',
            strokeWidth: 1
          }
        }]
      },

      title: {
        text: this.getTitle(),
        align: 'center',
        margin: 25,
        style: {
          whiteSpace: 'nowrap',
          textOverflow: 'ellipsis',
        }
      },

      credits: {
        text: 'Forecast from 2018',
        // href: this.xml.querySelector('credit link').getAttribute('url'),
        position: {
          x: -40
        }
      },

      tooltip: {
        shared: true,
        useHTML: true,
        headerFormat:
        '<small>{point.x:%A, %b %e, %H:%M} - {point.point.to:%H:%M}</small><br>' +
        '<b>{point.point.symbolName}</b><br>'

      },
      scrollbar: {
        barBackgroundColor: '#FFFFFF',
        enabled: true,
        zIndex: 200,
      },

      xAxis: [{ // Bottom X axis
        type: 'datetime',
        max: this.temperatures[this.temperatures.length - 1].x,
        min: this.temperatures[this.temperatures.length -120].x,
        scrollbar: {
          barBackgroundColor: '#FFFFFF',
          enabled: true,
          zIndex: 200,
        },
        tickInterval: 2 * 36e5, // two hours
        minorTickInterval: 36e5, // one hour
        tickLength: 0,
        gridLineWidth: 1,
        startOnTick: true,
        endOnTick: true,
        minPadding: 0,
        maxPadding: 0,
        offset: 30,
        showLastLabel: true,
        labels: {
          format: '{value:%H}'
        },
        crosshair: true,
        minRange: 3600 * 1000 // one hour
      }, { // Top X axis
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

      yAxis: [{ // temperature axis
        title: {
          text: null
        },
        max: 50,
        labels: {
          format: '{value}°',
          style: {
            fontSize: '10px'
          },
          x: -3
        },
        plotLines: [{ // zero plane
          value: 0,
          // color: '#BBBBBB',
          width: 1,
          zIndex: 2
        }],
        maxPadding: 0.3,
        minRange: 8,
        tickInterval: 1,
        // gridLineColor: (Highcharts.darkTheme && Highcharts.darkTheme.background2) || '#F0F0F0'

      }, { // precipitation axis
        title: {
          text: null
        },
        labels: {
          enabled: false
        },
        gridLineWidth: 0,
        tickLength: 0,
        minRange: 10,
        min: 0

      }, { // Air pressure
        allowDecimals: false,
        max: 1200,
        title: { // Title on top of axis
          text: 'hPa',
          offset: 0,
          align: 'high',
          rotation: 0,
          style: {
            fontSize: '12px',
            color: Highcharts.getOptions().colors[11]
          },
          textAlign: 'left',
          x: 3
        },
        labels: {
          style: {
            fontSize: '12px',
            color: Highcharts.getOptions().colors[11]
          },
          y: 2,
          x: 3
        },
        gridLineWidth: 0,
        opposite: true,
        showLastLabel: false
      }],

      legend: {
        enabled: false
      },

      plotOptions: {
        series: {
          pointPlacement: 'between',
          getExtremesFromAll: true
        }
      },


      series: [{
        name: 'Temperature',
        turboThreshold: 2000,
        data: this.temperatures,
        type: 'spline',
        marker: {
          enabled: true,
          states: {
            hover: {
              enabled: true
            }
          }
        },
        tooltip: {
          pointFormat: '<span style="color:{point.color}">\u25CF</span> ' +
          '{series.name}: <b>{point.value}°C</b><br/>'
        },
        zIndex: 1,
        color: '#FF3333',
        negativeColor: '#48AFE8'
      }, {
        name: 'Precipitation',
        turboThreshold: 2000,
        data: this.precipitationsError,
        type: 'column',
        color: 'url(#precipitation-error)',
        yAxis: 1,
        groupPadding: 0,
        pointPadding: 0,
        tooltip: {
          valueSuffix: ' mm',
          pointFormat: '<span style="color:{point.color}">\u25CF</span> ' +
          '{series.name}: <b>{point.minvalue} mm - {point.maxvalue} mm</b><br/>'
        },
        grouping: true,
        dataLabels: {
          enabled: true,
          formatter: function () {
            if (this.point.maxvalue > 0) {
              return this.point.maxvalue;
            }
          },
          style: {
            fontSize: '8px',
            color: 'gray'
          }
        }
      }, {
        name: 'Precipitation',
        turboThreshold: 2000,
        data: this.precipitations,
        type: 'column',
        color: '#68CFE8',
        yAxis: 1,
        groupPadding: 0,
        pointPadding: 0,
        grouping: true,
        dataLabels: {
          enabled: !false,
          formatter: function () {
            if (this.y > 0) {
              return this.y;
            }
          },
          style: {
            fontSize: '8px',
            color: 'gray'
          }
        },
        tooltip: {
          valueSuffix: ' mm'
        }
      }, {
        name: 'Air pressure',
        turboThreshold: 2000,
        color: Highcharts.getOptions().colors[11],
        data: this.pressures,
        marker: {
          enabled: true
        },
        shadow: false,
        tooltip: {
          valueSuffix: 'hPa'
        },
        dashStyle: 'shortdot',
        yAxis: 2
      }, {
        name: 'Wind',
        turboThreshold: 2000,
        type: 'windbarb',
        id: 'windbarbs',
        color: Highcharts.getOptions().colors[1],
        lineWidth: 1.5,
        data: this.winds,
        grouping: true,
        vectorLength: 18,
        yOffset: -15,
        xOffset: -7,
        tooltip: {
          valueSuffix: ' m/s'
        }
      }]
    };
  }

  /**
   * Get the title based on the XML data
   */
  getTitle() {
    let title = 'Meteogram ';
   // title += this.station.name ? 'for ' + this.station.name : 'station_X';
    //title += this.station.city ? ', ' + this.station.city : '';
    return title;
  }

  /**
   * Function to smooth the temperature line. The original data provides only whole degrees,
   * which makes the line graph look jagged. So we apply a running mean on it, but preserve
   * the unaltered value in the tooltip.
   */
  smoothLine(data) {
    let i = data.length;
    let sum;
    let value;

    while (i--) {
      data[i].value = value = data[i].y; // preserve value for tooltip

      // Set the smoothed value to the average of the closest points, but don't allow
      // it to differ more than 0.5 degrees from the given value
      sum = (data[i - 1] || data[i]).y + value + (data[i + 1] || data[i]).y;
      data[i].y = Math.max(value - 0.5, Math.min(sum / 3, value + 0.5));
    }
  }

  /**
   * Draw the weather symbols on top of the temperature series. The symbols are
   * fetched from yr.no's MIT licensed weather symbol collection.
   * https://github.com/YR/weather-symbols
   */
  drawWeatherSymbols(chart) {

    chart.series[0].data.forEach((point, i) => {
      if (this.resolution > 36e5 || i % 2 === 0) {
        const hour = moment(this.dates[i]).hour();
        const month = moment(this.dates[i]).month();
        let night = false;
        let symbole = this.symbols[i];

        if (
          ([12, 1, 2].includes(month) && [17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6].includes(hour)) ||
          ([3, 4, 5].includes(month) && [20, 21, 22, 23, 0, 1, 2, 3, 4, 5].includes(hour)) ||
          ([6, 7, 8].includes(month) && [22, 23, 0, 1, 2, 3, 4].includes(hour)) ||
          ([9, 10, 11].includes(month) && [20, 21, 22, 23, 0, 1, 2, 3, 4, 5].includes(hour))
        ) {
          night = true;
        }

        if (night && symbole === '01d') {
          symbole = '01n';
        }

        chart.renderer
          .image(
            'assets/images/' +
            symbole + '.svg',
            point.plotX + chart.plotLeft - 8,
            point.plotY + chart.plotTop - 30,
            30,
            30
          )
          .attr({
            zIndex: 5
          })
          .add();
      }
    });
  }

  /**
   * Draw blocks around wind arrows, below the plot area
   */
  drawBlocksForWindArrows(chart: ChartsMore) {
    const xAxis = chart.xAxis[0];
    let x;
    let pos;
    let max;
    let isLong;
    let isLast;
    let i;

    for (pos = xAxis.min, max = xAxis.max, i = 0; pos <= max + 36e5; pos += 36e5, i += 1) {
      // Get the X position
      isLast = pos === max + 36e5;
      x = Math.round(xAxis.toPixels(pos)) + (isLast ? 0.5 : -0.5);
      console.log('re ', this.resolution);
      // Draw the vertical dividers and ticks
      if (this.resolution > 36e5) {
        isLong = pos % this.resolution === 0;
      } else {
        isLong = i % 2 === 0;
      }
      chart.renderer.path(['M', x, chart.plotTop + chart.plotHeight + (isLong ? 0 : 24),
        'L', x, chart.plotTop + chart.plotHeight + 32, 'Z'])
        .attr({
          'stroke': chart.options.chart.plotBorderColor,
          'stroke-width': 1
        })
        .add();
    }

    // Center items in block
    chart.get('windbarbs').markerGroup.attr({
      translateX: chart.get('windbarbs').markerGroup.translateX
    });
  }

  createChart() {
    Highcharts.setOptions(darkTheme);
    this.chart = Highcharts.chart(this.renderMeteoGram(), (chart) => {
      this.onChartLoad(chart);
    });
  }

  initChart() {
    this.chart = null;
    this.dates = [];
    this.symbols = [];
    this.precipitations = [];
    this.precipitationsError = [];
    this.winds = [];
    this.temperatures = [];
    this.pressures = [];
  }

  destroyChart() {
    Highcharts.charts.pop();
  }


  onChartLoad(chart) {
    this.drawWeatherSymbols(chart);
    this.drawBlocksForWindArrows(chart);
  }

  error() {
    console.log('Failed loading data, please try again later');
  }
}
