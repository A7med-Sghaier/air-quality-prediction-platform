import {Component, OnInit} from '@angular/core';
import {StationPublisherService} from '../../_services/station-publisher.service';
import {Station} from '../../_models/Station';

@Component({
  selector: 'app-station-details',
  templateUrl: './station-details.component.html',
  styleUrls: ['./station-details.component.css']
})
export class StationDetailsComponent implements OnInit {
  station: Station | null = null;

  constructor(private stationPublisher: StationPublisherService) {
  }

  ngOnInit() {
    this.stationPublisher.getStationObservable()
      .subscribe(station => this.station = station);
  }
}
