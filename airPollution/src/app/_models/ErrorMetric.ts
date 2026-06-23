import {AirPollution, AirPollutionRaw} from './AirPollution';

export interface ErrorMetricRaw {
  key: string;
  name: string;
  short: string;
}

export class ErrorMetric {
  key: string;
  name: string;
  short: string;
}

export interface ErrorMetricValueRaw {
  name: string;
  type: string;
  values: {
    pm25: number;
    pm10: number;
    no2: number;
    co: number;
    o3: number;
    so2: number;
  };
}

export class ErrorMetricValue {
  name: string;
  type: string;
  airPollution: {
    pm25: number;
    pm10: number;
    no2: number;
    co: number;
    o3: number;
    so2: number;
  };
}
