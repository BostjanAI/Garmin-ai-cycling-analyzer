from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from cycling_analyzer.analyzer import ActivityAnalyzer
from cycling_analyzer.fit_parser import FitActivityParser
from scripts.generate_sample_fit import generate


@unittest.skipUnless(
    importlib.util.find_spec("garmin_fit_sdk"),
    "Polni FIT test zahteva deklarirani paket garmin-fit-sdk.",
)
class SampleFitIntegrationTest(unittest.TestCase):
    def test_official_sdk_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = generate(Path(directory) / "sample_ride.fit")
            parsed = FitActivityParser().parse(path)
            metrics = ActivityAnalyzer(max_heart_rate=190).analyze(parsed)

        self.assertEqual(metrics.distance_m, 30000.0)
        self.assertEqual(metrics.duration_s, 3600.0)
        self.assertEqual(len(metrics.records), 121)
        self.assertAlmostEqual(sum(metrics.hr_zones_s.values()), 3600.0)


if __name__ == "__main__":
    unittest.main()
