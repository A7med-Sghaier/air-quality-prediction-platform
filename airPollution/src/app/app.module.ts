import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { TabsModule } from 'ngx-bootstrap';

import { environment } from '../environments/environment';
import { WeatherService } from './_services/weather.service';
import { UrlBuilder } from './_helpers/http-req-builder';

import { AppComponent } from './app.component';
import { AgmCoreModule } from '@agm/core';
import { StationsMapComponent } from './_components/stations-map/stations-map.component';
import { WeatherChartComponent } from './_components/weather-chart/weather-chart.component';
import { PollutionChartComponent } from './_components/pollution-chart/pollution-chart.component';
import { PredictorsComponent } from './_components/predictors/predictors.component';
import { StationDetailsComponent } from './_components/station-details/station-details.component';
import { WeatherChartDirective } from './_directives/weather-chart.directive';
import { PollutionChartDirective } from './_directives/pollution-chart.directive';
import { PredictorsComparisonDirective } from './_directives/predictors-comparison.directive';
import { PredictorsComparisonSpiderwebDirective } from './_directives/predictors-comparison-spiderweb.directive';
import { MaterialModule } from './_modules/material.module';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {SynchronizedChartComponent} from './_components/synchronized-chart/synchronized-chart.component';
import {MeteogramComponent} from './_components/meteogram/meteogram.component';
import {SynchronizedChartService} from './_services/synchronized_chart_services.service';
import {SynchronizedStockService} from './_services/synchronized_stock_services.service';
import {PredictorsComparisonBcByPredDirective} from './_directives/predictors-comparison-bc-by-pred.directive';

@NgModule({
  declarations: [
    AppComponent,
    StationsMapComponent,
    WeatherChartComponent,
    PredictorsComponent,
    PollutionChartComponent,
    StationDetailsComponent,
    WeatherChartDirective,
    PollutionChartDirective,
    MeteogramComponent,
    SynchronizedChartComponent,
    PredictorsComparisonDirective,
    PredictorsComparisonSpiderwebDirective,
    PredictorsComparisonBcByPredDirective
  ],
  imports: [
    BrowserModule,
    CommonModule,
    FormsModule,
    HttpClientModule,
    AgmCoreModule.forRoot({
      apiKey: environment.googleMapsApiKey
    }),
    TabsModule.forRoot(),
    MaterialModule,
    BrowserAnimationsModule,
  ],
  providers: [WeatherService, UrlBuilder, SynchronizedChartService, SynchronizedStockService],
  bootstrap: [AppComponent]
})
export class AppModule {
}
