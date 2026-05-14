import sys
from pathlib import Path

# Allow this example to run from the repository without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from videoeventsql import VideoEventLogger


# This example saves an already-generated OpenCV-style motion result.
with VideoEventLogger("events.db") as logger:
    row_id = logger.log_detection(
        source="webcam_0",
        framework="opencv",
        frame_number=85,
        timestamp_seconds=2.8,
        label="motion",
        bbox=[40, 60, 210, 330],
        metadata={"contour_area": 1240, "threshold": 25},
    )

print(f"Saved detection row {row_id}")
