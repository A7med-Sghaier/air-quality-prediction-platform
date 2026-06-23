/*************************************************************
 * DataSc - ${FILE_NAME}
 *
 * created by : Ahmed Sghaier
 * created on : 29.04.18 - 20:23
 * version : 1.0
 * copyright : all right reserved 2018
 *************************************************************/
//chart-options
export const chartOptions = {
  legend: {
    display: false
  },
  scales: {
    xAxes: [{
      display: true
    }],
    yAxes: [{
      display: true
    }],
  },
  zoom:{
    enabled: true,
    mode: 'x'
  },
  pan:{
    enabled: true,
    mode: 'x'
  },
  showTooltips:{
    enabled: false
  }
}
