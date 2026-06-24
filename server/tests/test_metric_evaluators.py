import unittest

from air_pollution.common.metric_evaluators import MeanAbsoluteErrorEvaluator


class FakePredictionRepository:
    def __init__(self):
        self.calls = []

    def get_structured_predictions_for_station(self, station_name, predictor, from_date, to_date):
        self.calls.append({
            "station_name": station_name,
            "predictor": predictor,
            "from_date": from_date,
            "to_date": to_date,
        })
        return {
            "2018-05-01T00:00:00": {"pm25": 12, "pm10": 25, "o3": 30},
            "2018-05-01T01:00:00": {"pm25": 18, "pm10": 35, "o3": 0},
        }


class FakeStationsRepository:
    def __init__(self):
        self.calls = []

    def get_aq_histories_for_station(self, station_name, from_time, to_time):
        self.calls.append({
            "station_name": station_name,
            "from_time": from_time,
            "to_time": to_time,
        })
        return {
            "2018-05-01T00:00:00": {"pm25": 10, "pm10": 20, "o3": 40},
            "2018-05-01T01:00:00": {"pm25": 20, "pm10": 30, "o3": 10},
        }


class MetricEvaluatorTest(unittest.TestCase):
    def test_calculate_from_db_uses_injected_repositories(self):
        prediction_repository = FakePredictionRepository()
        stations_repository = FakeStationsRepository()
        evaluator = MeanAbsoluteErrorEvaluator(
            prediction_repository=prediction_repository,
            stations_repository=stations_repository,
        )

        result = evaluator.calculate_from_db(
            predictor="gradientboost",
            station_id="station-a",
            from_date="2018-05-01",
            to_date="2018-05-02",
        )

        self.assertEqual(result, {"pm25": 2, "pm10": 5, "o3": 10})
        self.assertEqual(prediction_repository.calls[0]["station_name"], "station-a")
        self.assertEqual(prediction_repository.calls[0]["predictor"], "gradientboost")
        self.assertEqual(stations_repository.calls[0]["station_name"], "station-a")


if __name__ == "__main__":
    unittest.main()
