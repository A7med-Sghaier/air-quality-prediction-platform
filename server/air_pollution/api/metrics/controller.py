from datetime import datetime, timedelta

import falcon
from bson.json_util import dumps
from dateutil.parser import parse

from air_pollution.common.metric_evaluators import (
    MaximumPercentageErrorEvaluator,
    MeanAbsoluteErrorEvaluator,
    MeanAbsolutePercentageErrorEvaluator,
    MeanSquaredErrorEvaluator,
    RootMeanSquaredErrorEvaluator,
    SymmetricMeanAbsolutePercentageErrorEvaluator,
)


DEFAULT_LOOKBACK_DAYS = 3000

METRIC_DEFINITIONS = [
    {
        'key': 'mean-absolute-error',
        'name': 'Mean absolute error',
        'short': 'MAE',
        'evaluator': MeanAbsoluteErrorEvaluator,
    },
    {
        'key': 'mean-absolute-percentage-error',
        'name': 'Mean absolute percentage error',
        'short': 'MAPE',
        'evaluator': MeanAbsolutePercentageErrorEvaluator,
    },
    {
        'key': 'symmetric-mean-absolute-percentage-error',
        'name': 'Symmetric mean absolute percentage error',
        'short': 'SMAPE',
        'evaluator': SymmetricMeanAbsolutePercentageErrorEvaluator,
    },
    {
        'key': 'maximum-percentage-error',
        'name': 'Maximum percentage error',
        'short': 'MPE',
        'evaluator': MaximumPercentageErrorEvaluator,
    },
    {
        'key': 'mean-squared-error',
        'name': 'Mean squared error',
        'short': 'MSE',
        'evaluator': MeanSquaredErrorEvaluator,
    },
    {
        'key': 'root-mean-squared-error',
        'name': 'Root mean squared error',
        'short': 'RMSE',
        'evaluator': RootMeanSquaredErrorEvaluator,
    },
]

METRICS_BY_KEY = {metric['key']: metric for metric in METRIC_DEFINITIONS}


class MetricsController(object):
    def on_get(self, req, res):
        res.body = dumps([
            {
                'key': metric['key'],
                'name': metric['name'],
                'short': metric['short'],
            }
            for metric in METRIC_DEFINITIONS
        ], ensure_ascii=False)
        res.status = falcon.HTTP_200


class StationMetricsController(object):
    def on_get(self, req, res, predictor, station_name):
        from_date, to_date = parse_metric_date_range(req)

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

        from_date, to_date = parse_metric_date_range(req)
        body = metric['evaluator']().calculate_from_db(
            station_id=station_name,
            from_date=from_date,
            to_date=to_date,
            predictor=predictor,
        )

        res.body = dumps(body, ensure_ascii=False)
        res.status = falcon.HTTP_200


def parse_metric_date_range(req):
    from_date = parse(req.params['from']) if 'from' in req.params else datetime.now() - timedelta(days=DEFAULT_LOOKBACK_DAYS)
    to_date = parse(req.params['to']) if 'to' in req.params else datetime.now()
    return from_date, to_date
