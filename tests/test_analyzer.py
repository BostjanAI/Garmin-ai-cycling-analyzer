from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from cycling_analyzer.analyzer import ActivityAnalyzer
from cycling_analyzer.models import ParsedActivity, RideRecord


class ActivityAnalyzerTest(unittest.TestCase):
    def setUp(self) -> None:
        start = datetime(2026, 10, 18, 8, tzinfo=UTC)
        self.records = [
            RideRecord(
                timestamp=start + timedelta(seconds=index * 10),
                heart_rate=100 + index * 10,
                cadence=80 + index,
                power=150 + index * 10,
                altitude_m=100 + [0, 5, 2, 12][index],
            )
            for index in range(4)
        ]
        self.activity = ParsedActivity(
            source_name="sample.fit",
            content_hash="abc",
            started_at=start,
            duration_s=30,
            distance_m=300,
            avg_speed_mps=None,
            avg_heart_rate=None,
            max_heart_rate=None,
            avg_cadence=None,
            total_ascent_m=None,
            avg_power=None,
            max_power=None,
            records=self.records,
        )

    def test_calculates_metrics_in_python(self) -> None:
        result = ActivityAnalyzer(max_heart_rate=200).analyze(self.activity)

        self.assertAlmostEqual(result.avg_speed_kmh, 36.0)
        self.assertAlmostEqual(result.avg_heart_rate, 115.0)
        self.assertEqual(result.max_heart_rate, 130)
        self.assertAlmostEqual(result.avg_power, 165.0)
        self.assertEqual(result.max_power, 180)
        self.assertAlmostEqual(result.elevation_gain_m, 15.0)
        self.assertEqual(sum(result.hr_zones_s.values()), 30.0)
        self.assertAlmostEqual(result.hr_change_pct, (125 - 105) / 105 * 100)

    def test_missing_sensor_data_remains_missing(self) -> None:
        self.activity.records = [RideRecord(timestamp=self.activity.started_at)]
        result = ActivityAnalyzer(max_heart_rate=190).analyze(self.activity)

        self.assertIsNone(result.avg_heart_rate)
        self.assertIsNone(result.avg_power)
        self.assertIsNone(result.elevation_gain_m)
        self.assertEqual(result.hr_zones_s, {"Z1": 0, "Z2": 0, "Z3": 0, "Z4": 0, "Z5": 0})


if __name__ == "__main__":
    unittest.main()

