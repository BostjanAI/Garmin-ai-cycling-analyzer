from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from cycling_analyzer.models import ActivityMetrics, RideRecord
from cycling_analyzer.repository import SQLiteActivityRepository


class SQLiteActivityRepositoryTest(unittest.TestCase):
    def test_round_trip_deduplication_and_delete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = SQLiteActivityRepository(Path(directory) / "test.db")
            started_at = datetime(2026, 10, 18, 8, tzinfo=UTC)
            metrics = ActivityMetrics(
                source_name="sample.fit",
                content_hash="same-content",
                started_at=started_at,
                duration_s=3600,
                distance_m=30000,
                avg_speed_kmh=30,
                avg_heart_rate=140,
                max_heart_rate=170,
                avg_cadence=82,
                elevation_gain_m=500,
                avg_power=None,
                max_power=None,
                hr_first_half=135,
                hr_second_half=145,
                hr_change_pct=7.4,
                hr_zones_s={"Z1": 60, "Z2": 600, "Z3": 1200, "Z4": 900, "Z5": 0},
                records=[RideRecord(timestamp=started_at, heart_rate=130)],
            )

            self.assertTrue(repository.add(metrics))
            self.assertFalse(repository.add(metrics))
            rows = repository.list_all()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["records"][0].heart_rate, 130)
            self.assertEqual(repository.delete_all(), 1)
            self.assertEqual(repository.list_all(), [])


if __name__ == "__main__":
    unittest.main()

