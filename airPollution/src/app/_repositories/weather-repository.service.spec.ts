import { TestBed, inject } from '@angular/core/testing';

import { WeatherRepositoryService } from './weather-repository.service';

describe('WeatherRepositoryService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [WeatherRepositoryService]
    });
  });

  it('should be created', inject([WeatherRepositoryService], (service: WeatherRepositoryService) => {
    expect(service).toBeTruthy();
  }));
});
