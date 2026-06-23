import {AirPollution, AirPollutionRaw} from './AirPollution';

export interface PredictionRaw {
  _id: {
    $oid: string
  };
  station_name: string;
  utc_time: {
    $date: number
  };
  prediction_type: string;
  air_quality: AirPollutionRaw;
}

export class Prediction {
  id: string;
  stationName: string;
  timestamp: Date;
  predictionType: string;
  airQuality: AirPollution;
}

export interface PredictorRaw {
  name: string;
}

export class Predictor {
  name: string;
}
