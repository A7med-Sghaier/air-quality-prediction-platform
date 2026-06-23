import { TestBed, inject } from '@angular/core/testing';

import { CityPublisherService } from './city-publisher.service';

describe('CityPublisherService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [CityPublisherService]
    });
  });

  it('should be created', inject([CityPublisherService], (service: CityPublisherService) => {
    expect(service).toBeTruthy();
  }));
});
