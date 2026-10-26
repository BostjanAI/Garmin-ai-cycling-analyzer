from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field

from .analyzer import ActivityAnalyzer
from .fit_parser import FitActivityParser
from .repository import SQLiteActivityRepository
from .sources import ActivitySource

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SyncResult:
    imported: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


class ActivitySyncService:
    def __init__(
        self,
        source: ActivitySource,
        parser: FitActivityParser,
        analyzer: ActivityAnalyzer,
        repository: SQLiteActivityRepository,
    ) -> None:
        self.source = source
        self.parser = parser
        self.analyzer = analyzer
        self.repository = repository

    def sync(self) -> SyncResult:
        result = SyncResult()
        for candidate in self.source.discover():
            try:
                digest = hashlib.sha256(candidate.local_path.read_bytes()).hexdigest()
                if self.repository.contains_hash(digest):
                    result.skipped += 1
                    continue
                parsed = self.parser.parse(candidate.local_path)
                if self.repository.add(self.analyzer.analyze(parsed)):
                    result.imported += 1
                else:
                    result.skipped += 1
            except Exception as error:  # posamezna datoteka ne ustavi celotne sinhronizacije
                logger.exception("Uvoz %s ni uspel", candidate.source_name)
                result.errors.append(f"{candidate.source_name}: {error}")
        return result

