from __future__ import annotations

import hashlib
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from cycling_analyzer.analyzer import ActivityAnalyzer
from cycling_analyzer.models import ParsedActivity
from cycling_analyzer.repository import SQLiteActivityRepository
from cycling_analyzer.sources.base import ActivityCandidate, ActivitySource
from cycling_analyzer.sync import ActivitySyncService


class FixedSource(ActivitySource):
    def __init__(self, path: Path) -> None:
        self.path = path

    def discover(self) -> list[ActivityCandidate]:
        return [ActivityCandidate(self.path.name, self.path)]


class FixedParser:
    def parse(self, path: Path) -> ParsedActivity:
        return ParsedActivity(
            source_name=path.name,
            content_hash=hashlib.sha256(path.read_bytes()).hexdigest(),
            started_at=datetime(2026, 10, 18, 8, tzinfo=UTC),
            duration_s=3600,
            distance_m=30000,
            avg_speed_mps=30 / 3.6,
            avg_heart_rate=140,
            max_heart_rate=170,
            avg_cadence=82,
            total_ascent_m=500,
            avg_power=None,
            max_power=None,
        )


class ActivitySyncServiceTest(unittest.TestCase):
    def test_second_sync_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = root / "sample.fit"
            sample.write_bytes(b"sample activity")
            repository = SQLiteActivityRepository(root / "test.db")
            service = ActivitySyncService(
                FixedSource(sample), FixedParser(), ActivityAnalyzer(190), repository
            )

            first = service.sync()
            second = service.sync()

            self.assertEqual((first.imported, first.skipped, first.errors), (1, 0, []))
            self.assertEqual((second.imported, second.skipped, second.errors), (0, 1, []))


if __name__ == "__main__":
    unittest.main()

