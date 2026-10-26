from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from cycling_analyzer.fit_parser import FitActivityParser, FitParseError


class StubFitParser(FitActivityParser):
    messages: dict
    errors: list[Exception]

    def _decode(self, path: Path):
        return self.messages, self.errors


class FitActivityParserTest(unittest.TestCase):
    def test_maps_fit_messages_and_ignores_missing_optional_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.fit"
            path.write_bytes(b"synthetic FIT fixture boundary")
            parser = StubFitParser()
            parser.errors = []
            parser.messages = {
                "session_mesgs": [
                    {
                        "start_time": datetime(2026, 10, 18, 8, tzinfo=UTC),
                        "total_timer_time": 60.0,
                        "total_distance": 500.0,
                        "enhanced_avg_speed": 8.333,
                        "avg_heart_rate": 130,
                    }
                ],
                "record_mesgs": [
                    {
                        "timestamp": datetime(2026, 10, 18, 8, tzinfo=UTC),
                        "heart_rate": 125,
                        "enhanced_speed": 8.0,
                    }
                ],
            }

            parsed = parser.parse(path)

        self.assertEqual(parsed.source_name, "sample.fit")
        self.assertEqual(parsed.distance_m, 500.0)
        self.assertEqual(parsed.avg_heart_rate, 130)
        self.assertIsNone(parsed.avg_power)
        self.assertEqual(parsed.records[0].heart_rate, 125)

    def test_reports_decoder_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.fit"
            path.write_bytes(b"broken")
            parser = StubFitParser()
            parser.messages = {}
            parser.errors = [RuntimeError("CRC Error")]
            with self.assertRaisesRegex(FitParseError, "CRC Error"):
                parser.parse(path)


if __name__ == "__main__":
    unittest.main()

