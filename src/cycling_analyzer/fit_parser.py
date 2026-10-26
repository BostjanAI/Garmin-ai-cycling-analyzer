from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import ParsedActivity, RideRecord


class FitParseError(ValueError):
    pass


class FitActivityParser:
    """Dekodira eno-sejno FIT aktivnost v notranji model faze 1."""

    def parse(self, path: Path) -> ParsedActivity:
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        messages, errors = self._decode(path)
        if errors:
            raise FitParseError(f"FIT dekodiranje ni uspelo: {errors[0]}")

        sessions = messages.get("session_mesgs", [])
        records = [self._record(item) for item in messages.get("record_mesgs", [])]
        records = [item for item in records if item is not None]
        if not sessions and not records:
            raise FitParseError("FIT datoteka ne vsebuje seje ali časovnih zapisov.")

        session: dict[str, Any] = sessions[0] if sessions else {}
        started_at = self._datetime(session.get("start_time"))
        if started_at is None and records:
            started_at = records[0].timestamp
        if started_at is None:
            raise FitParseError("Začetnega časa aktivnosti ni mogoče določiti.")

        duration_s = self._number(session.get("total_timer_time"))
        if duration_s is None and len(records) > 1:
            duration_s = (records[-1].timestamp - records[0].timestamp).total_seconds()
        distance_m = self._number(session.get("total_distance"))
        if distance_m is None and records:
            distances = [r.distance_m for r in records if r.distance_m is not None]
            if distances:
                distance_m = max(distances) - min(distances)

        return ParsedActivity(
            source_name=path.name,
            content_hash=content_hash,
            started_at=started_at,
            duration_s=duration_s,
            distance_m=distance_m,
            avg_speed_mps=self._first_number(session, "enhanced_avg_speed", "avg_speed"),
            avg_heart_rate=self._integer(session.get("avg_heart_rate")),
            max_heart_rate=self._integer(session.get("max_heart_rate")),
            avg_cadence=self._integer(session.get("avg_cadence")),
            total_ascent_m=self._number(session.get("total_ascent")),
            avg_power=self._integer(session.get("avg_power")),
            max_power=self._integer(session.get("max_power")),
            records=records,
        )

    @staticmethod
    def _decode(path: Path) -> tuple[dict[str, list[dict[str, Any]]], list[Exception]]:
        # Pozen uvoz omogoča zagon determinističnih testov in jasen opis manjkajoče
        # namestitve, še preden uporabnik prvič uvaža FIT datoteko.
        try:
            from garmin_fit_sdk import Decoder, Stream
        except ImportError as error:
            raise FitParseError(
                "Manjka paket garmin-fit-sdk. Zaženite: pip install -e ."
            ) from error
        decoder = Decoder(Stream.from_file(str(path)))
        return decoder.read()

    def _record(self, value: dict[str, Any]) -> RideRecord | None:
        timestamp = self._datetime(value.get("timestamp"))
        if timestamp is None:
            return None
        return RideRecord(
            timestamp=timestamp,
            heart_rate=self._integer(value.get("heart_rate")),
            cadence=self._integer(value.get("cadence")),
            power=self._integer(value.get("power")),
            speed_mps=self._first_number(value, "enhanced_speed", "speed"),
            altitude_m=self._first_number(value, "enhanced_altitude", "altitude"),
            distance_m=self._number(value.get("distance")),
        )

    @staticmethod
    def _datetime(value: Any) -> datetime | None:
        if not isinstance(value, datetime):
            return None
        return value if value.tzinfo else value.replace(tzinfo=UTC)

    @staticmethod
    def _number(value: Any) -> float | None:
        return float(value) if isinstance(value, (int, float)) else None

    @staticmethod
    def _integer(value: Any) -> int | None:
        return int(value) if isinstance(value, (int, float)) else None

    def _first_number(self, value: dict[str, Any], *keys: str) -> float | None:
        for key in keys:
            number = self._number(value.get(key))
            if number is not None:
                return number
        return None

