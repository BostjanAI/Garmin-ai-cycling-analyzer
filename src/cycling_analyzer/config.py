from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    database_path: Path
    fit_inbox: Path
    log_level: str
    max_heart_rate: int

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv()
        max_hr = int(os.getenv("MAX_HEART_RATE", "190"))
        if not 100 <= max_hr <= 240:
            raise ValueError("MAX_HEART_RATE mora biti med 100 in 240.")
        return cls(
            database_path=Path(os.getenv("DATABASE_PATH", "data/cycling_analyzer.db")),
            fit_inbox=Path(os.getenv("FIT_INBOX", "fit_inbox")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            max_heart_rate=max_hr,
        )

