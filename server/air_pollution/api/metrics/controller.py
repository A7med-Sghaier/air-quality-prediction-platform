import falcon
from dateutil.parser import parse
from bson.json_util import dumps
from datetime import datetime, timedelta

from air_pollution.common.metric_evaluators import MeanAbsoluteErrorEvaluator, MeanAbsolutePercentageErrorEvaluator, \
    MaximumPercentageErrorEvaluator, RootMeanSquaredErrorEvaluator, MeanSquaredErrorEvaluator, \
    SymmetricMeanAbsolutePercentageErrorEvaluator


class MetricsController(object):
    def on_get(self, req, res):
        res.body = dumps([
            {
                'key': 'mean-absolute-error',
                'name': 'Mean absolute error',
                'short': 'MAE'
            },
            {
                'key': 'mean-absolute-percentage-error',
                'name': 'Mean absolute percentage error',
                'short': 'MAPE'
            },
            {
                'key': 'symmetric-mean-absolute-percentage-error',
                'name': 'Symmetric mean absolute percentage error',
                'short': 'SMAPE'
            },
            {
                'key': 'maximum-percentage-error',
                'name': 'Maximum percentage error',
                'short': 'MPE'
            },
            {
                'key': 'mean-squared-error',
                'name': 'Mean squared error',
                'short': 'MSE'
            },
            {
                'key': 'root-mean-squared-error',
                'name': 'Root mean squared error',
                'short': 'RMSE'
            },
        ], ensure_ascii=False)
        res.status = falcon.HTTP_200


class StationMetricsController(object):
    def on_get(self, req, res, predictor, station_name):
        if 'from' in req.params:
            from_date = parse(req.params['from'])
        else:
            from_date = datetime.now() - timedelta(days=3000)

        if 'to' in req.params:
            to_date = parse(req.params['to'])
        else:
            to_date = datetime.now()

        body = []
        mean_absolute_error = MeanAbsoluteErrorEvaluator().calculate_from_db(station_id=station_name,
                                                                             from_date=from_date,
                                                                             to_date=to_date, predictor=predictor)
        mean_absolute_percentage_error = MeanAbsolutePercentageErrorEvaluator().calculate_from_db(
            station_id=station_name,
            from_date=from_date,
            to_date=to_date,
            predictor=predictor)
        maximum_percentage_error = MaximumPercentageErrorEvaluator().calculate_from_db(station_id=station_name,
                                                                                       from_date=from_date,
                                                                                       to_date=to_date,
                                                                                       predictor=predictor)
        mean_squared_error = MeanSquaredErrorEvaluator().calculate_from_db(station_id=station_name, from_date=from_date,
                                                                           to_date=to_date, predictor=predictor)
        root_mean_squared_error = RootMeanSquaredErrorEvaluator().calculate_from_db(station_id=station_name,
                                                                                    from_date=from_date,
                                                                                    to_date=to_date,
                                                                                    predictor=predictor)
        smape = SymmetricMeanAbsolutePercentageErrorEvaluator().calculate_from_db(station_id=station_name,
                                                                                  from_date=from_date,
                                                                                  to_date=to_date,
                                                                                  predictor=predictor)

        body.append({
            'name': 'mean-absolute-error',
            'type': 'mean-absolute-error',
            'values': mean_absolute_error
        })
        body.append({
            'name': 'mean-absolute-percentage-error',
            'type': 'mean-absolute-percentage-error',
            'values': mean_absolute_percentage_error
        })
        body.append({
            'name': 'symmetric-mean-absolute-percentage-error',
            'type': 'symmetric-mean-absolute-percentage-error',
            'values': smape
        })
        body.append({
            'name': 'maximum-percentage-error',
            'type': 'maximum-percentage-error',
            'values': maximum_percentage_error
        })
        body.append({
            'name': 'mean-squared-error',
            'type': 'mean-squared-error',
            'values': mean_squared_error
        })
        body.append({
            'name': 'root-mean-squared-error',
            'type': 'root-mean-squared-error',
            'values': root_mean_squared_error
        })

        res.body = dumps(body, ensure_ascii=False)
        res.status = falcon.HTTP_200


class MetricController(object):
    def on_get(self, req, res, predictor, station_name, metric_name):
        if 'from' in req.params:
            from_date = parse(req.params['from'])
        else:
            from_date = datetime.now() - timedelta(days=3000)

        if 'to' in req.params:
            to_date = parse(req.params['to'])
        else:
            to_date = datetime.now()

        if metric_name == 'mean-absolute-error':
            body = MeanAbsoluteErrorEvaluator().calculate(station_id=station_name, from_date=from_date, to_date=to_date,
                                                          predictor=predictor)
        elif metric_name == 'mean-absolute-percentage-error':
            body = MeanAbsoluteErrorEvaluator().calculate(station_id=station_name, from_date=from_date, to_date=to_date,
                                                          predictor=predictor)
        elif metric_name == 'maximum-percentage-error':
            body = MaximumPercentageErrorEvaluator().calculate(station_id=station_name, from_date=from_date,
                                                               to_date=to_date,
                                                               predictor=predictor)
        elif metric_name == 'root-mean-squared-error':
            body = RootMeanSquaredErrorEvaluator().calculate(station_id=station_name, from_date=from_date,
                                                             to_date=to_date, predictor=predictor)
        elif metric_name == 'mean-squared-error':
            body = MeanSquaredErrorEvaluator().calculate(station_id=station_name, from_date=from_date,
                                                         to_date=to_date, predictor=predictor)
        else:
            res.body = dumps({'error': metric_name + ' not known!'})
            res.status = falcon.HTTP_400
            return

        res.body = dumps(body, ensure_ascii=False)
        res.status = falcon.HTTP_200
