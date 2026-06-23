import math
import unittest

from air_pollution.common.metrics import (
    aligned_prediction_pairs,
    maximum_percentage_error_by_key,
    mean_absolute_error_by_key,
    mean_absolute_percentage_error_by_key,
    mean_squared_error_by_key,
    root_mean_squared_error_by_key,
    sanitized_values,
    symmetric_mean_absolute_percentage_error_by_key,
)


class MetricCalculationTest(unittest.TestCase):
    def setUp(self):
        self.keys = ("pm25", "pm10", "o3")
        self.predictions = {
            "2018-05-01T00:00:00": {"pm25": 12, "pm10": 25, "o3": 30},
            "2018-05-01T01:00:00": {"pm25": 18, "pm10": 35, "o3": 0},
            "missing-history": {"pm25": 999, "pm10": 999, "o3": 999},
        }
        self.histories = {
            "2018-05-01T00:00:00": {"pm25": 10, "pm10": 20, "o3": 40},
            "2018-05-01T01:00:00": {"pm25": 20, "pm10": 30, "o3": 10},
        }

    def test_sanitized_values_fills_missing_none_and_nan_values(self):
        result = sanitized_values(self.keys, {"pm25": None, "pm10": math.nan})

        self.assertEqual(result, {"pm25": 0, "pm10": 0, "o3": 0})

    def test_aligned_prediction_pairs_skips_predictions_without_history(self):
        predictions, histories = aligned_prediction_pairs(self.keys, self.predictions, self.histories)

        self.assertEqual(len(predictions), 2)
        self.assertEqual(len(histories), 2)
        self.assertEqual(predictions[0]["pm25"], 12)
        self.assertEqual(histories[0]["pm25"], 10)

    def test_mean_absolute_error_by_key(self):
        result = mean_absolute_error_by_key(self.predictions, self.histories, self.keys)

        self.assertEqual(result, {"pm25": 2, "pm10": 5, "o3": 10})

    def test_mean_squared_error_by_key(self):
        result = mean_squared_error_by_key(self.predictions, self.histories, self.keys)

        self.assertEqual(result, {"pm25": 4, "pm10": 25, "o3": 100})

    def test_root_mean_squared_error_by_key(self):
        result = root_mean_squared_error_by_key(self.predictions, self.histories, self.keys)

        self.assertEqual(result, {"pm25": 2, "pm10": 5, "o3": 10})

    def test_mean_absolute_percentage_error_by_key_skips_zero_values(self):
        result = mean_absolute_percentage_error_by_key(self.predictions, self.histories, self.keys)

        self.assertEqual(result["pm25"], 15)
        self.assertAlmostEqual(result["pm10"], 20.8333333333)
        self.assertEqual(result["o3"], 25)

    def test_symmetric_mean_absolute_percentage_error_by_key_skips_zero_values(self):
        result = symmetric_mean_absolute_percentage_error_by_key(self.predictions, self.histories, self.keys)

        self.assertAlmostEqual(result["pm25"], 14.3540669856)
        self.assertAlmostEqual(result["pm10"], 18.8034188034)
        self.assertAlmostEqual(result["o3"], 28.5714285714)

    def test_maximum_percentage_error_by_key(self):
        result = maximum_percentage_error_by_key(self.predictions, self.histories, self.keys)

        self.assertEqual(result["pm25"], 20)
        self.assertAlmostEqual(result["pm10"], 25)
        self.assertEqual(result["o3"], 25)


if __name__ == "__main__":
    unittest.main()
