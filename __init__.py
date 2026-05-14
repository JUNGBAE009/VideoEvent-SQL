from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


__all__ = ["VideoEventLogger"]


# Only these framework names are accepted in v0.1.
ALLOWED_FRAMEWORKS = {"yolo", "opencv", "numpy", "custom"}

# SQLite creates the table automatically when the logger starts.
DETECTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    framework TEXT NOT NULL,
    frame_number INTEGER,
    timestamp_seconds REAL,
    label TEXT NOT NULL,
    confidence REAL,
    x1 REAL,
    y1 REAL,
    x2 REAL,
    y2 REAL,
    width REAL,
    height REAL,
    metadata_json TEXT,
    created_at TEXT NOT NULL
);
"""


class VideoEventLogger:
    def __init__(self, db_path: str | Path = "events.db") -> None:
        self.db_path = Path(db_path)

        # If the user passes "data/events.db", create "data/" first.
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection: sqlite3.Connection | None = None
        self._create_detections_table()

    def log_detection(
        self,
        source: str,
        framework: str,
        label: str,
        frame_number: int | None = None,
        timestamp_seconds: float | None = None,
        confidence: float | None = None,
        bbox: list[float] | tuple[float, float, float, float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        # Validate required text fields before writing anything to SQLite.
        source = self._validate_non_empty_string(source, "source")
        framework = self._validate_framework(framework)
        label = self._validate_non_empty_string(label, "label")

        if confidence is not None:
            confidence = self._validate_number(confidence, "confidence")

        # bbox is optional. When present, it is [x1, y1, x2, y2].
        x1, y1, x2, y2, width, height = self._validate_bbox(bbox)

        metadata_json: str | None = None
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise ValueError("metadata must be a dict when provided")

            # Store extra information as JSON text so SQLite can keep it in one column.
            metadata_json = json.dumps(metadata, ensure_ascii=False)

        # UTC timestamps make rows easier to compare across machines.
        created_at = datetime.now(timezone.utc).isoformat()

        # Use ? placeholders so user values are passed safely as parameters.
        cursor = self._get_connection().execute(
            """
            INSERT INTO detections (
                source,
                framework,
                frame_number,
                timestamp_seconds,
                label,
                confidence,
                x1,
                y1,
                x2,
                y2,
                width,
                height,
                metadata_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                framework,
                frame_number,
                timestamp_seconds,
                label,
                confidence,
                x1,
                y1,
                x2,
                y2,
                width,
                height,
                metadata_json,
                created_at,
            ),
        )

        # Commit immediately so the saved row is durable after this call returns.
        self._get_connection().commit()
        return int(cursor.lastrowid)

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> "VideoEventLogger":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def _get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            # Open the SQLite database file only when a connection is needed.
            self._connection = sqlite3.connect(self.db_path)
        return self._connection

    def _create_detections_table(self) -> None:
        connection = self._get_connection()
        connection.execute(DETECTIONS_TABLE_SQL)
        connection.commit()

    @staticmethod
    def _validate_non_empty_string(value: str, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string")
        return value.strip()

    @classmethod
    def _validate_framework(cls, framework: str) -> str:
        # Normalize values like "YOLO" to "yolo".
        framework = cls._validate_non_empty_string(framework, "framework").lower()
        if framework not in ALLOWED_FRAMEWORKS:
            allowed = ", ".join(sorted(ALLOWED_FRAMEWORKS))
            raise ValueError(f"framework must be one of: {allowed}")
        return framework

    @staticmethod
    def _validate_number(value: object, field_name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} must be numeric")
        return float(value)

    @classmethod
    def _validate_bbox(
        cls,
        bbox: list[float] | tuple[float, float, float, float] | None,
    ) -> tuple[float | None, float | None, float | None, float | None, float | None, float | None]:
        if bbox is None:
            return None, None, None, None, None, None

        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            raise ValueError("bbox must be a list or tuple with exactly 4 numeric values")

        x1, y1, x2, y2 = (cls._validate_number(value, "bbox value") for value in bbox)

        # Width and height are derived from the two bbox corners.
        width = x2 - x1
        height = y2 - y1
        return x1, y1, x2, y2, width, height
