from __future__ import annotations

from statistics import fmean

from .models import ActivityMetrics, ParsedActivity, RideRecord


class ActivityAnalyzer:
    def __init__(self, max_heart_rate: int, max_sample_gap_s: float = 30.0) -> None:
        self.max_heart_rate = max_heart_rate
        self.max_sample_gap_s = max_sample_gap_s

    def analyze(self, activity: ParsedActivity) -> ActivityMetrics:
        heart_rates = [r.heart_rate for r in activity.records if r.heart_rate is not None]
        cadences = [r.cadence for r in activity.records if r.cadence is not None]
        powers = [r.power for r in activity.records if r.power is not None]
        avg_hr = self._mean_or(heart_rates, activity.avg_heart_rate)
        avg_cadence = self._mean_or(cadences, activity.avg_cadence)
        avg_power = self._mean_or(powers, activity.avg_power)
        max_hr = max(heart_rates) if heart_rates else activity.max_heart_rate
        max_power = max(powers) if powers else activity.max_power

        avg_speed = activity.avg_speed_mps
        if avg_speed is None and activity.distance_m is not None and activity.duration_s:
            avg_speed = activity.distance_m / activity.duration_s

        elevation = activity.total_ascent_m
        if elevation is None:
            elevation = self._elevation_gain(activity.records)

        first_hr, second_hr = self._heart_rate_halves(activity.records)
        change = None
        if first_hr not in (None, 0) and second_hr is not None:
            change = (second_hr - first_hr) / first_hr * 100

        return ActivityMetrics(
            source_name=activity.source_name,
            content_hash=activity.content_hash,
            started_at=activity.started_at,
            duration_s=activity.duration_s,
            distance_m=activity.distance_m,
            avg_speed_kmh=avg_speed * 3.6 if avg_speed is not None else None,
            avg_heart_rate=avg_hr,
            max_heart_rate=max_hr,
            avg_cadence=avg_cadence,
            elevation_gain_m=elevation,
            avg_power=avg_power,
            max_power=max_power,
            hr_first_half=first_hr,
            hr_second_half=second_hr,
            hr_change_pct=change,
            hr_zones_s=self._heart_rate_zones(activity.records),
            records=activity.records,
        )

    @staticmethod
    def _mean_or(values: list[int], fallback: int | None) -> float | None:
        return fmean(values) if values else float(fallback) if fallback is not None else None

    @staticmethod
    def _elevation_gain(records: list[RideRecord]) -> float | None:
        altitudes = [r.altitude_m for r in records if r.altitude_m is not None]
        if len(altitudes) < 2:
            return None
        pairs = zip(altitudes, altitudes[1:])
        return sum(max(0.0, current - previous) for previous, current in pairs)

    @staticmethod
    def _heart_rate_halves(records: list[RideRecord]) -> tuple[float | None, float | None]:
        with_hr = [r for r in records if r.heart_rate is not None]
        if len(with_hr) < 2:
            return None, None
        midpoint = with_hr[0].timestamp + (with_hr[-1].timestamp - with_hr[0].timestamp) / 2
        first = [r.heart_rate for r in with_hr if r.timestamp <= midpoint]
        second = [r.heart_rate for r in with_hr if r.timestamp > midpoint]
        return (fmean(first) if first else None, fmean(second) if second else None)

    def _heart_rate_zones(self, records: list[RideRecord]) -> dict[str, float]:
        zones = {f"Z{number}": 0.0 for number in range(1, 6)}
        ordered = sorted(records, key=lambda record: record.timestamp)
        for current, following in zip(ordered, ordered[1:]):
            if current.heart_rate is None:
                continue
            seconds = (following.timestamp - current.timestamp).total_seconds()
            if seconds <= 0:
                continue
            seconds = min(seconds, self.max_sample_gap_s)
            ratio = current.heart_rate / self.max_heart_rate
            if ratio < 0.60:
                zone = "Z1"
            elif ratio < 0.70:
                zone = "Z2"
            elif ratio < 0.80:
                zone = "Z3"
            elif ratio < 0.90:
                zone = "Z4"
            else:
                zone = "Z5"
            zones[zone] += seconds
        return zones

