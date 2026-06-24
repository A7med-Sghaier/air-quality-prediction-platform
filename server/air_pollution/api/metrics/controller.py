import falcon
from bson.json_util import dumps

from air_pollution.api.metrics.registry import (
    METRIC_DEFINITIONS,
    METRICS_BY_KEY,
    parse_metric_date_range,
    public_metric_definitions,
)


class MetricsController(object):
    def on_get(self, req, res):
        res.body = dumps(public_metric_definitions(), ensure_ascii=False)
        res.status = falcon.HTTP_200


class StationMetricsController(object):
    def on_get(self, req, res, predictor, station_name):
        from_date, to_date = parse_metric_date_range(req.params)

        body = []
        for metric in METRIC_DEFINITIONS:
            values = metric['evaluator']().calculate_from_db(
                station_id=station_name,
                from_date=from_date,
                to_date=to_date,
                predictor=predictor,
            )
            body.append({
                'name': metric['key'],
                'type': metric['key'],
                'values': values,
            })

        res.body = dumps(body, ensure_ascii=False)
        res.status = falcon.HTTP_200


class MetricController(object):
    def on_get(self, req, res, predictor, station_name, metric_name):
        metric = METRICS_BY_KEY.get(metric_name)
        if metric is None:
            res.body = dumps({'error': metric_name + ' not known!'})
            res.status = falcon.HTTP_400
            return

        from_date, to_date = parse_metric_date_range(req.params)
        body = metric['evaluator']().calculate_from_db(
            station_id=station_name,
            from_date=from_date,
            to_date=to_date,
            predictor=predictor,
        )

        res.body = dumps(body, ensure_ascii=False)
        res.status = falcon.HTTP_200
