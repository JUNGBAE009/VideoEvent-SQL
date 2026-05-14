import sys
from pathlib import Path

# Allow this example to run from the repository without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from videoeventsql import VideoEventLogger


# This example saves an already-generated YOLO-style detection result.
with VideoEventLogger("events.db") as logger:
    row_id = logger.log_detection(
        source="sample.mp4",
        framework="yolo",
        frame_number=120,
        timestamp_seconds=4.0,
        label="person",
        confidence=0.94,
        bbox=[100, 80, 320, 460],
        metadata={"model": "yolov8n.pt"},
    )

print(f"Saved detection row {row_id}")
