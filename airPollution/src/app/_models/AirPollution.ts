export enum PollutionAttribute {
  PM25 = 'pm25',
  PM10 = 'pm10',
  NO2 = 'no2',
  CO = 'co',
  O3 = 'o3',
  SO2 = 'so2',
}

export const PollutionAttributes = [
  PollutionAttribute.PM25,
  PollutionAttribute.PM10,
  PollutionAttribute.O3,
  PollutionAttribute.NO2,
  PollutionAttribute.CO,
  PollutionAttribute.SO2,
];

export interface AirPollutionRaw {
  pm25: number;
  pm10: number;
  no2: number;
  co: number;
  o3: number;
  so2: number;
  timestamp: {
    $date: number
  };
}

export class AirPollution {
  pm25: number;
  pm10: number;
  no2: number;
  co: number;
  o3: number;
  so2: number;
  timestamp: Date;
}
