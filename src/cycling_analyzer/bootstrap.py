from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .analyzer import ActivityAnalyzer
from .config import Settings
from .fit_parser import FitActivityParser
from .repository import SQLiteActivityRepository
from .sources import FitDirectorySource
from .sync import ActivitySyncService


def configure_logging(level: str) -> None:
    Path("logs").mkdir(exist_ok=True)
    handler = RotatingFileHandler(
        "logs/cycling_analyzer.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[handler, logging.StreamHandler()],
        force=True,
    )


def build_repository(settings: Settings) -> SQLiteActivityRepository:
    repository = SQLiteActivityRepository(settings.database_path)
    repository.initialize()
    return repository


def build_sync_service(settings: Settings) -> ActivitySyncService:
    return ActivitySyncService(
        source=FitDirectorySource(settings.fit_inbox),
        parser=FitActivityParser(),
        analyzer=ActivityAnalyzer(settings.max_heart_rate),
        repository=build_repository(settings),
    )

