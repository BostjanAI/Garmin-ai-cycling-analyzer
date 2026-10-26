from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ActivityCandidate:
    source_name: str
    local_path: Path


class ActivitySource(ABC):
    """Zamenljiva meja za FIT mapo, Garmin Personal API ali poslovni API."""

    @abstractmethod
    def discover(self) -> list[ActivityCandidate]:
        """Vrne lokalno dostopne kandidate za uvoz."""

