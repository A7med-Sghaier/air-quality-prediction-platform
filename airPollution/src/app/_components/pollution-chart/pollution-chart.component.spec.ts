import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PollutionChartComponent } from './pollution-chart.component';

describe('PollutionChartComponent', () => {
  let component: PollutionChartComponent;
  let fixture: ComponentFixture<PollutionChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PollutionChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PollutionChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
