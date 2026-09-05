import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "stage": getattr(record, "stage", "general"),
            "message": record.getMessage(),
        }

        if hasattr(record, "details"):
            entry["details"] = record.details

        return json.dumps(entry)


def get_logger(
    name: str = "incubrix",
    log_path: str = "logs/pipeline.jsonl",
) -> logging.Logger:
    """Create a structured JSONL logger."""

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    output = Path(log_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(
        output,
        encoding="utf-8",
    )

    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

    return logger


def log_stage(
    logger: logging.Logger,
    stage: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Write a structured pipeline event."""

    extra = {
        "stage": stage,
        "details": details or {},
    }

    logger.info(
        message,
        extra=extra,
    )