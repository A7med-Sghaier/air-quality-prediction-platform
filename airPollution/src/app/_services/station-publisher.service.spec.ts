import { TestBed, inject } from '@angular/core/testing';

import { StationPublisherService } from './station-publisher.service';

describe('StationPublisherService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [StationPublisherService]
    });
  });

  it('should be created', inject([StationPublisherService], (service: StationPublisherService) => {
    expect(service).toBeTruthy();
  }));
});
