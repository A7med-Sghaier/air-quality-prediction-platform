"""Metric evaluator classes used by the API layer.

The evaluators are intentionally thin: repositories load prediction/history
data, while :mod:`air_pollution.common.metrics` owns the pure metric math.
Keeping that boundary small makes the calculations easy to unit test without
MongoDB or the historical ML dependencies.
"""

from air_pollution.common.metrics import (
    DEFAULT_KEYS,
    aligned_prediction_pairs,
    maximum_percentage_error_by_key,
    mean_absolute_error_by_key,
    mean_absolute_percentage_error_by_key,
    mean_squared_error_by_key,
    root_mean_squared_error_by_key,
    sanitized_values,
    symmetric_mean_absolute_percentage_error_by_key,
)
from air_pollution.common.repositories import PredictionRepository, StationsRepository


KEYS = list(DEFAULT_KEYS)


def fill_up_keys(keys, values):
    """Backward-compatible wrapper for older callers."""
    return sanitized_values(keys, values)


def map_history_on_predictions(keys, predictions, histories):
    """Backward-compatible wrapper for older callers."""
    return aligned_prediction_pairs(keys, predictions, histories)


class MetricEvaluator:
    """Base class for metrics calculated from prediction and history series."""

    metric_function = None

    def __init__(self, prediction_repository=None, stations_repository=None):
        self.keys = KEYS
        self.prediction_repository = prediction_repository or PredictionRepository()
        self.stations_repository = stations_repository or StationsRepository()

    def calculate_from_db(self, predictor, station_id, from_date, to_date):
        """Load station data from repositories and calculate the configured metric."""
        predictions = self.prediction_repository.get_structured_predictions_for_station(
            station_name=station_id,
            predictor=predictor,
            from_date=from_date,
            to_date=to_date,
        )
        histories = self.stations_repository.get_aq_histories_for_station(
            station_name=station_id,
            from_time=from_date,
            to_time=to_date,
        )

        return self.calculate(predictions, histories)

    def calculate(self, predictions, true_values):
        if self.metric_function is None:
            raise NotImplementedError("MetricEvaluator subclasses must define metric_function")

        return self.metric_function(predictions, true_values, self.keys)


class MeanAbsoluteErrorEvaluator(MetricEvaluator):
    metric_function = staticmethod(mean_absolute_error_by_key)


class MeanAbsolutePercentageErrorEvaluator(MetricEvaluator):
    metric_function = staticmethod(mean_absolute_percentage_error_by_key)


class SymmetricMeanAbsolutePercentageErrorEvaluator(MetricEvaluator):
    metric_function = staticmethod(symmetric_mean_absolute_percentage_error_by_key)


class MaximumPercentageErrorEvaluator(MetricEvaluator):
    metric_function = staticmethod(maximum_percentage_error_by_key)


class MeanSquaredErrorEvaluator(MetricEvaluator):
    metric_function = staticmethod(mean_squared_error_by_key)


class RootMeanSquaredErrorEvaluator(MetricEvaluator):
    metric_function = staticmethod(root_mean_squared_error_by_key)
