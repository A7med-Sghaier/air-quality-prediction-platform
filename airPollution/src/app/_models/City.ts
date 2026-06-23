export class City {
  private readonly _name: string;
  private readonly _long: number;
  private readonly _lat: number;

  constructor(name: string, long: number, lat: number) {
    this._name = name;
    this._long = long;
    this._lat = lat;
  }

  get name(): string {
    return this._name;
  }

  get long(): number {
    return this._long;
  }

  get lat(): number {
    return this._lat;
  }
}

export const CITIES = [
  new City('London', -0.118092, 51.509865),
  new City('Beijing', 116.3636, 39.913818),
];
