from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import ActivityMetrics, RideRecord


class SQLiteActivityRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_hash TEXT NOT NULL UNIQUE,
                    source_name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    duration_s REAL,
                    distance_m REAL,
                    avg_speed_kmh REAL,
                    avg_heart_rate REAL,
                    max_heart_rate INTEGER,
                    avg_cadence REAL,
                    elevation_gain_m REAL,
                    avg_power REAL,
                    max_power INTEGER,
                    hr_first_half REAL,
                    hr_second_half REAL,
                    hr_change_pct REAL,
                    hr_zones_json TEXT NOT NULL,
                    records_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def contains_hash(self, content_hash: str) -> bool:
        self.initialize()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM activities WHERE content_hash = ?", (content_hash,)
            ).fetchone()
        return row is not None

    def add(self, metrics: ActivityMetrics) -> bool:
        self.initialize()
        values = (
            metrics.content_hash,
            metrics.source_name,
            metrics.started_at.isoformat(),
            metrics.duration_s,
            metrics.distance_m,
            metrics.avg_speed_kmh,
            metrics.avg_heart_rate,
            metrics.max_heart_rate,
            metrics.avg_cadence,
            metrics.elevation_gain_m,
            metrics.avg_power,
            metrics.max_power,
            metrics.hr_first_half,
            metrics.hr_second_half,
            metrics.hr_change_pct,
            json.dumps(metrics.hr_zones_s),
            json.dumps([record.to_dict() for record in metrics.records]),
        )
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO activities (
                    content_hash, source_name, started_at, duration_s, distance_m,
                    avg_speed_kmh, avg_heart_rate, max_heart_rate, avg_cadence,
                    elevation_gain_m, avg_power, max_power, hr_first_half,
                    hr_second_half, hr_change_pct, hr_zones_json, records_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
        return cursor.rowcount == 1

    def list_all(self) -> list[dict[str, Any]]:
        self.initialize()
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM activities ORDER BY started_at DESC"
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["hr_zones_s"] = json.loads(item.pop("hr_zones_json"))
            item["records"] = [
                RideRecord.from_dict(record) for record in json.loads(item.pop("records_json"))
            ]
            result.append(item)
        return result

    def delete_all(self) -> int:
        self.initialize()
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM activities")
        return cursor.rowcount

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

