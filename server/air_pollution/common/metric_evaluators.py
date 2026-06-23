import math
from air_pollution.common.repositories import PredictionRepository, StationsRepository
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt

KEYS = ['pm25', 'pm10', 'o3']


def map_history_on_predictions(keys, predictions, histories):
    """
    Iterates over the predictions and creates an array

    :param keys: All keys we want to fill up
    :param predictions: a dict of all predictions where the key is the predicted time and the value the actual prediction
    :param histories: a dict of the real history where the key is the predicted time and the value the actual values
    :return:
    """
    preds = []
    hist = []
    for time, prediction in predictions.items():
        if time not in histories:
            continue
        preds.append(fill_up_keys(keys, prediction))
        hist.append(fill_up_keys(keys, histories[time]))

    return preds, hist


def fill_up_keys(keys, dict):
    """
    Fills up all the given keys in the given dict. If a key is missing or nan
    it will fill it with zero.

    :param keys: All keys we want to fill up
    :param dict: the dict we want to fill up
    :return:
    """
    for key in keys:
        if key not in dict or dict[key] is None or math.isnan(dict[key]):
            dict[key] = 0
    return dict


class MeanAbsoluteErrorEvaluator:
    prediction_repository = None
    stations_repository = None

    def __init__(self):
        self.prediction_repository = PredictionRepository()
        self.stations_repository = StationsRepository()

    def calculate_from_db(self, predictor, station_id, from_date, to_date):
        """
        Calculates the metric for the given predictor with values from the db of the given timeframe.

        :param predictor: the predictor we want to evaluate
        :param station_id: the station for which we want to create the evaluation
        :param from_date: the start date of the time frame
        :param to_date: the end date of the time frame
        :return:
        """
        predictions = self.prediction_repository.get_structured_predictions_for_station(station_name=station_id,
                                                                                        predictor=predictor,
                                                                                        from_date=from_date,
                                                                                        to_date=to_date)
        histories = self.stations_repository.get_aq_histories_for_station(station_name=station_id, from_time=from_date,
                                                                          to_time=to_date)

        return self.calculate(predictions, histories)

    def calculate(self, predictions, true_values):
        """
        Calculates the metric for all values with the given predictions and true values.
        :param predictions: an dict with all predictions where the key is the time as sting and the value are the predicted keys.
        :param true_values: an dict with all true values where the key is the time as sting and the value are the actual values.
        :return: a dict with all keys and the corresponding metrics
        """
        mapped_predictions, mapped_history = map_history_on_predictions(KEYS, predictions, true_values)
        result = fill_up_keys(KEYS, {})
        for key in KEYS:
            preds = list(map(lambda x: x[key], mapped_predictions))
            hist = list(map(lambda x: x[key], mapped_history))
            result[key] = mean_absolute_error(hist, preds)

        return result


class MeanAbsolutePercentageErrorEvaluator:
    prediction_repository = None
    stations_repository = None

    def __init__(self):
        self.keys = KEYS
        self.prediction_repository = PredictionRepository()
        self.stations_repository = StationsRepository()

    def calculate_from_db(self, predictor, station_id, from_date, to_date):
        """
        Calculates the metric for the given predictor with values from the db of the given timeframe.

        :param predictor: the predictor we want to evaluate
        :param station_id: the station for which we want to create the evaluation
        :param from_date: the start date of the time frame
        :param to_date: the end date of the time frame
        :return:
        """
        predictions = self.prediction_repository.get_structured_predictions_for_station(station_name=station_id,
                                                                                        predictor=predictor,
                                                                                        from_date=from_date,
                                                                                        to_date=to_date)
        histories = self.stations_repository.get_aq_histories_for_station(station_name=station_id, from_time=from_date,
                                                                          to_time=to_date)

        return self.calculate(predictions, histories)

    def calculate(self, predictions, true_values):
        """
        Calculates the metric for all values with the given predictions and true values.

        :param predictions: an dict with all predictions where the key is the time as sting and the value are the predicted keys.
        :param true_values: an dict with all true values where the key is the time as sting and the value are the actual values.
        :return: a dict with all keys and the corresponding metrics
        """
        result = fill_up_keys(self.keys, {})
        count = fill_up_keys(self.keys, {})
        for time, prediction in predictions.items():
            if time not in true_values:
                continue

            prediction = fill_up_keys(self.keys, prediction)
            actual = fill_up_keys(self.keys, true_values[time])

            for key in self.keys:
                if actual[key] == 0 or prediction[key] == 0:
                    continue

                count[key] += 1
                result[key] += abs(prediction[key] - actual[key]) / actual[key] * 100

        for key in self.keys:
            if count[key] == 0:
                continue
            result[key] /= count[key]

        return result


class SymmetricMeanAbsolutePercentageErrorEvaluator:
    prediction_repository = None
    stations_repository = None

    def __init__(self):
        self.keys = KEYS
        self.prediction_repository = PredictionRepository()
        self.stations_repository = StationsRepository()

    def calculate_from_db(self, predictor, station_id, from_date, to_date):
        """
        Calculates the metric for the given predictor with values from the db of the given timeframe.

        :param predictor: the predictor we want to evaluate
        :param station_id: the station for which we want to create the evaluation
        :param from_date: the start date of the time frame
        :param to_date: the end date of the time frame
        :return:
        """
        predictions = self.prediction_repository.get_structured_predictions_for_station(station_name=station_id,
                                                                                        predictor=predictor,
                                                                                        from_date=from_date,
                                                                                        to_date=to_date)
        histories = self.stations_repository.get_aq_histories_for_station(station_name=station_id, from_time=from_date,
                                                                          to_time=to_date)

        return self.calculate(predictions, histories)

    def calculate(self, predictions, true_values):
        """
        Calculates the metric for all values with the given predictions and true values.

        :param predictions: an dict with all predictions where the key is the time as sting and the value are the predicted keys.
        :param true_values: an dict with all true values where the key is the time as sting and the value are the actual values.
        :return: a dict with all keys and the corresponding metrics
        """
        result = fill_up_keys(self.keys, {})
        count = fill_up_keys(self.keys, {})
        for time, prediction in predictions.items():
            if time not in true_values:
                continue

            prediction = fill_up_keys(self.keys, prediction)
            actual = fill_up_keys(self.keys, true_values[time])

            for key in self.keys:
                if actual[key] == 0 or prediction[key] == 0:
                    continue

                count[key] += 1
                result[key] += abs(prediction[key] - actual[key]) / ((abs(actual[key]) + abs(prediction[key])) / 2)

        for key in self.keys:
            if count[key] == 0:
                continue
            result[key] *= 100
            result[key] /= count[key]

        return result


class MaximumPercentageErrorEvaluator:
    prediction_repository = None
    stations_repository = None

    def __init__(self):
        self.keys = KEYS
        self.prediction_repository = PredictionRepository()
        self.stations_repository = StationsRepository()

    def calculate_from_db(self, predictor, station_id, from_date, to_date):
        """
        Calculates the metric for the given predictor with values from the db of the given timeframe.

        :param predictor: the predictor we want to evaluate
        :param station_id: the station for which we want to create the evaluation
        :param from_date: the start date of the time frame
        :param to_date: the end date of the time frame
        :return:
        """
        predictions = self.prediction_repository.get_structured_predictions_for_station(station_name=station_id,
                                                                                        predictor=predictor,
                                                                                        from_date=from_date,
                                                                                        to_date=to_date)
        histories = self.stations_repository.get_aq_histories_for_station(station_name=station_id, from_time=from_date,
                                                                          to_time=to_date)

        return self.calculate(predictions, histories)

    def calculate(self, predictions, true_values):
        """
        Calculates the metric for all values with the given predictions and true values.

        :param predictions: an dict with all predictions where the key is the time as sting and the value are the predicted keys.
        :param true_values: an dict with all true values where the key is the time as sting and the value are the actual values.
        :return: a dict with all keys and the corresponding metrics
        """
        result = fill_up_keys(self.keys, {})
        for time, prediction in predictions.items():
            if time not in true_values:
                continue

            prediction = fill_up_keys(self.keys, prediction)
            actual = fill_up_keys(self.keys, true_values[time])

            for key in self.keys:
                if actual[key] == 0 or prediction[key] == 0:
                    continue

                number = abs(prediction[key] - actual[key]) / actual[key] * 100
                result[key] = result[key] if result[key] >= number else number

        return result


class MeanSquaredErrorEvaluator:
    prediction_repository = None
    stations_repository = None

    def __init__(self):
        self.keys = KEYS
        self.prediction_repository = PredictionRepository()
        self.stations_repository = StationsRepository()

    def calculate_from_db(self, predictor, station_id, from_date, to_date):
        """
        Calculates the metric for the given predictor with values from the db of the given timeframe.

        :param predictor: the predictor we want to evaluate
        :param station_id: the station for which we want to create the evaluation
        :param from_date: the start date of the time frame
        :param to_date: the end date of the time frame
        :return:
        """
        predictions = self.prediction_repository.get_structured_predictions_for_station(station_name=station_id,
                                                                                        predictor=predictor,
                                                                                        from_date=from_date,
                                                                                        to_date=to_date)
        histories = self.stations_repository.get_aq_histories_for_station(station_name=station_id, from_time=from_date,
                                                                          to_time=to_date)

        return self.calculate(predictions, histories)

    def calculate(self, predictions, true_values):
        """
        Calculates the metric for all values with the given predictions and true values.

        :param predictions: an dict with all predictions where the key is the time as sting and the value are the predicted keys.
        :param true_values: an dict with all true values where the key is the time as sting and the value are the actual values.
        :return: a dict with all keys and the corresponding metrics
        """
        mapped_predictions, mapped_history = map_history_on_predictions(KEYS, predictions, true_values)
        result = fill_up_keys(KEYS, {})
        for key in KEYS:
            preds = list(map(lambda x: x[key], mapped_predictions))
            hist = list(map(lambda x: x[key], mapped_history))
            result[key] = mean_squared_error(hist, preds)

        return result


class RootMeanSquaredErrorEvaluator:
    prediction_repository = None
    stations_repository = None

    def __init__(self):
        self.keys = KEYS
        self.prediction_repository = PredictionRepository()
        self.stations_repository = StationsRepository()

    def calculate_from_db(self, predictor, station_id, from_date, to_date):
        """
        Calculates the metric for the given predictor with values from the db of the given timeframe.

        :param predictor: the predictor we want to evaluate
        :param station_id: the station for which we want to create the evaluation
        :param from_date: the start date of the time frame
        :param to_date: the end date of the time frame
        :return:
        """
        predictions = self.prediction_repository.get_structured_predictions_for_station(station_name=station_id,
                                                                                        predictor=predictor,
                                                                                        from_date=from_date,
                                                                                        to_date=to_date)
        histories = self.stations_repository.get_aq_histories_for_station(station_name=station_id, from_time=from_date,
                                                                          to_time=to_date)

        return self.calculate(predictions, histories)

    def calculate(self, predictions, true_values):
        """
        Calculates the metric for all values with the given predictions and true values.

        :param predictions: an dict with all predictions where the key is the time as sting and the value are the predicted keys.
        :param true_values: an dict with all true values where the key is the time as sting and the value are the actual values.
        :return: a dict with all keys and the corresponding metrics
        """
        mapped_predictions, mapped_history = map_history_on_predictions(KEYS, predictions, true_values)
        result = fill_up_keys(KEYS, {})
        for key in KEYS:
            preds = list(map(lambda x: x[key], mapped_predictions))
            hist = list(map(lambda x: x[key], mapped_history))
            result[key] = sqrt(mean_squared_error(hist, preds))

        return result
