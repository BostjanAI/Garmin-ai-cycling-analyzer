from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class RideRecord:
    timestamp: datetime
    heart_rate: int | None = None
    cadence: int | None = None
    power: int | None = None
    speed_mps: float | None = None
    altitude_m: float | None = None
    distance_m: float | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["timestamp"] = self.timestamp.isoformat()
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> RideRecord:
        return cls(**{**value, "timestamp": datetime.fromisoformat(value["timestamp"])})


@dataclass(slots=True)
class ParsedActivity:
    source_name: str
    content_hash: str
    started_at: datetime
    duration_s: float | None
    distance_m: float | None
    avg_speed_mps: float | None
    avg_heart_rate: int | None
    max_heart_rate: int | None
    avg_cadence: int | None
    total_ascent_m: float | None
    avg_power: int | None
    max_power: int | None
    records: list[RideRecord] = field(default_factory=list)


@dataclass(slots=True)
class ActivityMetrics:
    source_name: str
    content_hash: str
    started_at: datetime
    duration_s: float | None
    distance_m: float | None
    avg_speed_kmh: float | None
    avg_heart_rate: float | None
    max_heart_rate: int | None
    avg_cadence: float | None
    elevation_gain_m: float | None
    avg_power: float | None
    max_power: int | None
    hr_first_half: float | None
    hr_second_half: float | None
    hr_change_pct: float | None
    hr_zones_s: dict[str, float]
    records: list[RideRecord]

