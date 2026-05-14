import sys
from pathlib import Path

# Allow this example to run from the repository without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from videoeventsql import VideoEventLogger


# This example saves an already-generated NumPy-style analysis result.
with VideoEventLogger("events.db") as logger:
    row_id = logger.log_detection(
        source="array_analysis",
        framework="numpy",
        frame_number=20,
        timestamp_seconds=0.66,
        label="motion_score",
        confidence=0.77,
        metadata={"mean_diff": 18.4, "max_diff": 120},
    )

print(f"Saved detection row {row_id}")
