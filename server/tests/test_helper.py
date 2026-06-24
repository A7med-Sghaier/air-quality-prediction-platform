import math
import unittest

from air_pollution.common.helper import (
    fill_up_air_pollution_keys,
    get_pipeline_map,
    normalize_months,
)


class HelperTest(unittest.TestCase):
    def test_fill_up_air_pollution_keys_fills_missing_none_and_nan(self):
        values = {"pm25": None, "pm10": math.nan, "o3": 12}

        result = fill_up_air_pollution_keys(("pm25", "pm10", "o3", "no2"), values, default=-1)

        self.assertIs(result, values)
        self.assertEqual(result, {"pm25": -1, "pm10": -1, "o3": 12, "no2": -1})

    def test_normalize_months_represents_month_as_unit_circle_coordinates(self):
        sin_value, cos_value = normalize_months(3)

        self.assertAlmostEqual(sin_value, 1)
        self.assertAlmostEqual(cos_value, 0)

    def test_get_pipeline_map_builds_history_projection(self):
        result = get_pipeline_map("aq_histories", "air_quality")

        self.assertEqual(result["$project"]["histories"]["$map"]["input"], "$aq_histories")
        self.assertEqual(
            result["$project"]["histories"]["$map"]["in"]["$mergeObjects"][1],
            "$$history.air_quality",
        )


if __name__ == "__main__":
    unittest.main()
