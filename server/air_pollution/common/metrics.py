"""Pure metric calculations for air-quality predictions.

The API evaluators load data from MongoDB, but the actual metric math should
stay independent from persistence so it can be tested quickly and reused by
CLI, API, or notebook workflows.
"""

import math
from typing import Callable, Dict, Iterable, List, Mapping, Tuple


DEFAULT_KEYS = ("pm25", "pm10", "o3")


MetricValues = Dict[str, float]
TimeSeries = Mapping[str, Mapping[str, float]]


def sanitized_values(keys: Iterable[str], values: Mapping[str, float]) -> MetricValues:
    """Return metric values for all keys, replacing missing/empty values with 0."""
    result = {}
    for key in keys:
        value = values.get(key)
        if value is None or _is_nan(value):
            result[key] = 0
        else:
            result[key] = value
    return result


def aligned_prediction_pairs(
    keys: Iterable[str],
    predictions: TimeSeries,
    histories: TimeSeries,
) -> Tuple[List[MetricValues], List[MetricValues]]:
    """Align prediction and history entries by timestamp and normalize keys."""
    normalized_predictions = []
    normalized_histories = []

    for timestamp, prediction in predictions.items():
        if timestamp not in histories:
            continue

        normalized_predictions.append(sanitized_values(keys, prediction))
        normalized_histories.append(sanitized_values(keys, histories[timestamp]))

    return normalized_predictions, normalized_histories


def mean_absolute_error_by_key(
    predictions: TimeSeries,
    histories: TimeSeries,
    keys: Iterable[str] = DEFAULT_KEYS,
) -> MetricValues:
    return _calculate_average_error(predictions, histories, keys, lambda predicted, actual: abs(predicted - actual))


def mean_squared_error_by_key(
    predictions: TimeSeries,
    histories: TimeSeries,
    keys: Iterable[str] = DEFAULT_KEYS,
) -> MetricValues:
    return _calculate_average_error(predictions, histories, keys, lambda predicted, actual: (predicted - actual) ** 2)


def root_mean_squared_error_by_key(
    predictions: TimeSeries,
    histories: TimeSeries,
    keys: Iterable[str] = DEFAULT_KEYS,
) -> MetricValues:
    mse = mean_squared_error_by_key(predictions, histories, keys)
    return {key: math.sqrt(value) for key, value in mse.items()}


def mean_absolute_percentage_error_by_key(
    predictions: TimeSeries,
    histories: TimeSeries,
    keys: Iterable[str] = DEFAULT_KEYS,
) -> MetricValues:
    return _calculate_percentage_error(
        predictions,
        histories,
        keys,
        lambda predicted, actual: abs(predicted - actual) / actual * 100,
    )


def symmetric_mean_absolute_percentage_error_by_key(
    predictions: TimeSeries,
    histories: TimeSeries,
    keys: Iterable[str] = DEFAULT_KEYS,
) -> MetricValues:
    return _calculate_percentage_error(
        predictions,
        histories,
        keys,
        lambda predicted, actual: abs(predicted - actual) / ((abs(actual) + abs(predicted)) / 2) * 100,
    )


def maximum_percentage_error_by_key(
    predictions: TimeSeries,
    histories: TimeSeries,
    keys: Iterable[str] = DEFAULT_KEYS,
) -> MetricValues:
    keys = tuple(keys)
    result = _zero_values(keys)

    normalized_predictions, normalized_histories = aligned_prediction_pairs(keys, predictions, histories)
    for prediction, actual in zip(normalized_predictions, normalized_histories):
        for key in keys:
            if actual[key] == 0 or prediction[key] == 0:
                continue

            error = abs(prediction[key] - actual[key]) / actual[key] * 100
            result[key] = max(result[key], error)

    return result


def _calculate_average_error(
    predictions: TimeSeries,
    histories: TimeSeries,
    keys: Iterable[str],
    error_function: Callable[[float, float], float],
) -> MetricValues:
    keys = tuple(keys)
    result = _zero_values(keys)
    count = _zero_values(keys)

    normalized_predictions, normalized_histories = aligned_prediction_pairs(keys, predictions, histories)
    for prediction, actual in zip(normalized_predictions, normalized_histories):
        for key in keys:
            result[key] += error_function(prediction[key], actual[key])
            count[key] += 1

    return {key: result[key] / count[key] if count[key] else 0 for key in keys}


def _calculate_percentage_error(
    predictions: TimeSeries,
    histories: TimeSeries,
    keys: Iterable[str],
    error_function: Callable[[float, float], float],
) -> MetricValues:
    keys = tuple(keys)
    result = _zero_values(keys)
    count = _zero_values(keys)

    normalized_predictions, normalized_histories = aligned_prediction_pairs(keys, predictions, histories)
    for prediction, actual in zip(normalized_predictions, normalized_histories):
        for key in keys:
            if actual[key] == 0 or prediction[key] == 0:
                continue

            result[key] += error_function(prediction[key], actual[key])
            count[key] += 1

    return {key: result[key] / count[key] if count[key] else 0 for key in keys}


def _zero_values(keys: Iterable[str]) -> MetricValues:
    return {key: 0 for key in keys}


def _is_nan(value: float) -> bool:
    try:
        return math.isnan(value)
    except TypeError:
        return False
