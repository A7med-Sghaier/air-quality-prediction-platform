import { TestBed, inject } from '@angular/core/testing';

import { PredictorsRepositoryService } from './predictors-repository.service';

describe('PredictorsRepositoryService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [PredictorsRepositoryService]
    });
  });

  it('should be created', inject([PredictorsRepositoryService], (service: PredictorsRepositoryService) => {
    expect(service).toBeTruthy();
  }));
});
