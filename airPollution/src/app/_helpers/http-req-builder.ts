/***********************************************
 * DataSc - http-req-builder
 * created by : AHMED SGHAIER
 * created on : 29.04.18 - 19:46
 * copyright : all right reserved @LMU 2018
 ***********************************************/
import {Injectable} from '@angular/core';
import {environment} from '../../environments/environment';

@Injectable()
export class UrlBuilder {
  private readonly apiBaseUrl: string;

  constructor() {
    this.apiBaseUrl = environment.api.url;
  }

  buildRequestUrl(serverRoute: string) {
    const route = serverRoute.startsWith('/') ? serverRoute : '/' + serverRoute;
    return `${this.apiBaseUrl}/api${route}`;
  }
}


