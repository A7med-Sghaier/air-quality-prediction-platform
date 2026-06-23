import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SynchronizedChartComponent } from './synchronized-chart.component';

describe('SynchronizedChartComponent', () => {
  let component: SynchronizedChartComponent;
  let fixture: ComponentFixture<SynchronizedChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SynchronizedChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SynchronizedChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
