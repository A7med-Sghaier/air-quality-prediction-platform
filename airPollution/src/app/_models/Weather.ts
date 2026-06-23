export enum WeatherAttribute {
  TEMPERATURE = 'Temperature',
  HUMIDITY = 'Humidity',
  PRESSURE = 'Pressure',
  WIND_SPEED = 'Wind Speed',
}

export const WeatherAttributes = [
  WeatherAttribute.TEMPERATURE,
  WeatherAttribute.HUMIDITY,
  WeatherAttribute.PRESSURE,
  WeatherAttribute.WIND_SPEED,
];

export class Weather {
  temperature: number;
  pressure: number;
  humidity: number;
  wind_speed: number;
  wind_dire: number
  weather: string;
  timestamp: Date;
}

export interface WeatherRaw {
  temperature: number;
  pressure: number;
  humidity: number;
  wind_speed: number;
  wind_dire: number;
  weather: string;
  timestamp: {
    $date: number;
  };
}

export interface WeatherData {
  temperature: number[];
  humidity: number[];
  pressure: number[];
  wind: number[];
  windDirections: number[];
  weatherDates: number[];
  weather: string[];
}

export class WeatherData implements WeatherData {
  temperature: number[];
  humidity: number[];
  pressure: number[];
  wind: number[];
  weatherDates: number[];
  windDirections: number[];
  weather: string[];

  constructor(options: {temperature?: number[], humidity?: number[], pressure?: number[], weather?: string[], wind?: number[], windDirections?: number[], weatherDates?: number[]} = {}) {
    this.temperature = options.temperature || [];
    this.humidity = options.humidity || [];
    this.pressure = options.pressure || [];
    this.wind = options.wind || [];
    this.windDirections = options.windDirections || [];
    this.weatherDates = options.weatherDates || [];
    this.weather = options.weather || [];
  }

  isEmpty(): boolean {
    return this.humidity.length === 0 && this.temperature.length === 0 && this.pressure.length === 0
      && this.wind.length === 0 && this.windDirections.length === 0 && this.weatherDates.length === 0;
  }

  getTemperature(): number[] {
    return this.temperature;
  }

  getHumidity(): number[] {
    return this.humidity;
  }

  getPressure(): number[] {
    return this.pressure;
  }

  getWind(): number[] {
    return this.wind;
  }

  getWeather(): string[] {
    return this.weather;
  }

  getWindDirections(): number[] {
    return this.windDirections;
  }

  getWeatherDates(): number[] {
    return this.weatherDates ;
  }

  setTemperature(temperature: number[]) {
    this.temperature = temperature;
  }

  setHumidity(humidity: number[]) {
    this.humidity = humidity;
  }

  setPressure(temperature: number[]) {
    this.pressure = temperature;
  }

  setWind(wind: number[]) {
    this.wind = wind;
  }

  setWindDirections(windDire: number[]) {
    this.windDirections = windDire;
  }

  setWeatherDates(weatherDates: number[]) {
    this.weatherDates = weatherDates;
  }

  setWeather(weather: string[]) {
    this.weather = weather;
  }
}
