"""Dependency-light metric registry for API controllers and tests."""

from datetime import datetime, timedelta

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


def public_metric_definitions():
    """Return serializable metric metadata without evaluator classes."""
    return [
        {
            'key': metric['key'],
            'name': metric['name'],
            'short': metric['short'],
        }
        for metric in METRIC_DEFINITIONS
    ]


def parse_metric_date_range(params, now=None):
    now = now or datetime.now()
    from_date = parse(params['from']) if 'from' in params else now - timedelta(days=DEFAULT_LOOKBACK_DAYS)
    to_date = parse(params['to']) if 'to' in params else now
    return from_date, to_date
