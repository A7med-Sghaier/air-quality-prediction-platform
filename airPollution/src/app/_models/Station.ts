export interface StationRaw {
  _id: {
    $oid: string,
  };
  name: string;
  station_type: string;
  longitude: number;
  latitude: null;
  city: string;
  location_type: string;
  is_grid: boolean;
  need_prediction: boolean;
}

export enum StationType {
  AQ,
  MEO,
}

export class Station {
  _id: string;
  name: string;
  stationType: StationType;
  longitude: number;
  latitude: null;
  city: string;
  location_type: string;
  is_grid: boolean;
  need_prediction: boolean;

  isAqStation(): boolean {
    return this.stationType === StationType.AQ;
  }
}
