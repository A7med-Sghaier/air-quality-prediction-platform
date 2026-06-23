import {TestBed, inject} from '@angular/core/testing';

import {ErrorMetricRepositoryService} from './error-metric-repository.service';

describe('ErrorMetricRepositoryService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ErrorMetricRepositoryService]
    });
  });

  it('should be created', inject([ErrorMetricRepositoryService], (service: ErrorMetricRepositoryService) => {
    expect(service).toBeTruthy();
  }));
});
