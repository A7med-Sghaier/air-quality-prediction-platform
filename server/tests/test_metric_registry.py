import unittest
from datetime import datetime, timedelta

from air_pollution.api.metrics.registry import (
    DEFAULT_LOOKBACK_DAYS,
    METRICS_BY_KEY,
    parse_metric_date_range,
    public_metric_definitions,
)
from air_pollution.common.metric_evaluators import (
    MeanAbsoluteErrorEvaluator,
    MeanAbsolutePercentageErrorEvaluator,
)


class MetricRegistryTest(unittest.TestCase):
    def test_metric_registry_maps_keys_to_correct_evaluators(self):
        self.assertIs(METRICS_BY_KEY["mean-absolute-error"]["evaluator"], MeanAbsoluteErrorEvaluator)
        self.assertIs(
            METRICS_BY_KEY["mean-absolute-percentage-error"]["evaluator"],
            MeanAbsolutePercentageErrorEvaluator,
        )

    def test_public_metric_definitions_exclude_evaluator_classes(self):
        definitions = public_metric_definitions()

        self.assertEqual(definitions[0]["key"], "mean-absolute-error")
        self.assertNotIn("evaluator", definitions[0])

    def test_parse_metric_date_range_uses_explicit_params(self):
        from_date, to_date = parse_metric_date_range({
            "from": "2018-05-01T00:00:00",
            "to": "2018-05-02T00:00:00",
        })

        self.assertEqual(from_date, datetime(2018, 5, 1, 0, 0))
        self.assertEqual(to_date, datetime(2018, 5, 2, 0, 0))

    def test_parse_metric_date_range_uses_default_lookback(self):
        now = datetime(2018, 5, 2, 12, 0)
        from_date, to_date = parse_metric_date_range({}, now=now)

        self.assertEqual(from_date, now - timedelta(days=DEFAULT_LOOKBACK_DAYS))
        self.assertEqual(to_date, now)


if __name__ == "__main__":
    unittest.main()
