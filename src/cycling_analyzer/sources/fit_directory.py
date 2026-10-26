from __future__ import annotations

from pathlib import Path

from .base import ActivityCandidate, ActivitySource


class FitDirectorySource(ActivitySource):
    def __init__(self, inbox: Path) -> None:
        self.inbox = inbox

    def discover(self) -> list[ActivityCandidate]:
        self.inbox.mkdir(parents=True, exist_ok=True)
        return [
            ActivityCandidate(source_name=path.name, local_path=path)
            for path in sorted(self.inbox.glob("*.fit"))
            if path.is_file()
        ]

