
# VideoEventSQL

A small Python library for saving video AI results in SQL.

VideoEventSQL stores already-generated YOLO, OpenCV, NumPy, or custom video AI results in a local SQLite database. It does not run YOLO, OpenCV, or NumPy for you. It only saves the results you already have.

## Final Shape

The runtime library is one importable folder:

```text
videoeventsql/
└── __init__.py
```

All v0.1 runtime code is inside `videoeventsql/__init__.py`. This keeps the library small while still allowing direct folder-copy usage in another Python project.

## Use In Another Project Without Installing

Copy the `videoeventsql/` folder into your project root. This is the simplest way to use VideoEventSQL in another project:

```text
my-project/
├── main.py
└── videoeventsql/
    └── __init__.py
```

Then import it normally:

```python
from videoeventsql import VideoEventLogger

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

print(row_id)
```

Run your script:

```bash
python3 main.py
```

This creates `events.db`, creates the `detections` table, and saves one row.

If you want the database in a separate folder, pass a path like `data/events.db`. VideoEventSQL will create the `data/` folder automatically if it does not exist.

## If You Copy The Whole Repository Folder

If you copy the whole `videoevent-sql/` repository folder into another project, Python will not automatically import from it because the outer folder name contains a hyphen. The direct-copy folder is the inner `videoeventsql/` folder.

Recommended:

```text
my-project/
├── main.py
└── videoeventsql/
    └── __init__.py
```

Alternative if you keep the whole repository under `vendor/`:

```text
my-project/
├── main.py
└── vendor/
    └── videoevent-sql/
        └── videoeventsql/
            └── __init__.py
```

Then add that repository folder to `sys.path` before importing:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "vendor" / "videoevent-sql"))

from videoeventsql import VideoEventLogger
```

For the cleanest usage, copy only `videoeventsql/` into the project root.

## Optional Local Installation

This project is not published to PyPI. If you want editable local installation:

```bash
cd /path/to/videoevent-sql
python3 --version
python3 -m pip install -e .
```

Use Python 3.10 or newer. The `-e` flag points Python at this local folder, so edits are reflected without reinstalling.

## What It Does

- Creates a SQLite database automatically.
- Creates a `detections` table automatically.
- Saves source, framework, frame number, timestamp, label, confidence, bounding box, metadata, and creation time.
- Uses SQLite parameter placeholders instead of SQL string formatting.
- Uses only the Python standard library.

## What It Does Not Do

- It does not run YOLO inference.
- It does not run OpenCV video processing.
- It does not run NumPy analysis.
- It does not provide query helpers, exports, dashboards, CLI commands, APIs, authentication, or cloud features.

## Security Notes

- SQLite writes use parameterized `?` placeholders, not SQL string formatting.
- This library does not open network connections, run shell commands, or load model files.
- The SQLite database is a local file. Do not pass an untrusted user-controlled path as `db_path` in web apps or services.
- `metadata` is stored as JSON text. Do not put secrets, API keys, tokens, passwords, or private personal data in metadata unless you are comfortable storing them in a local SQLite file.

## How It Works

`VideoEventLogger("events.db")` stores the database path, creates the parent directory if needed, opens a SQLite connection, and runs:

```sql
CREATE TABLE IF NOT EXISTS detections (...)
```

`log_detection()` then:

- validates `source`, `framework`, and `label`
- normalizes `framework` to lowercase
- allows only `yolo`, `opencv`, `numpy`, or `custom`
- validates `confidence` when provided
- validates `bbox` as four numeric values when provided
- calculates `width = x2 - x1`
- calculates `height = y2 - y1`
- serializes `metadata` with `json.dumps(metadata, ensure_ascii=False)`
- inserts the row with `?` placeholders
- commits the transaction
- returns the inserted row id

In short, your AI/video code creates the result, and VideoEventSQL only stores that result.

Use the context manager form to close the SQLite connection automatically:

```python
with VideoEventLogger("events.db") as logger:
    logger.log_detection(source="camera_1", framework="custom", label="event")
```

## YOLO-Style Example

```python
from videoeventsql import VideoEventLogger

with VideoEventLogger("events.db") as logger:
    logger.log_detection(
        source="sample.mp4",
        framework="yolo",
        frame_number=120,
        timestamp_seconds=4.0,
        label="person",
        confidence=0.94,
        bbox=[100, 80, 320, 460],
        metadata={"model": "yolov8n.pt"},
    )
```

## OpenCV-Style Example

```python
from videoeventsql import VideoEventLogger

with VideoEventLogger("events.db") as logger:
    logger.log_detection(
        source="webcam_0",
        framework="opencv",
        frame_number=85,
        timestamp_seconds=2.8,
        label="motion",
        bbox=[40, 60, 210, 330],
        metadata={"contour_area": 1240, "threshold": 25},
    )
```

## NumPy-Style Example

```python
from videoeventsql import VideoEventLogger

with VideoEventLogger("events.db") as logger:
    logger.log_detection(
        source="array_analysis",
        framework="numpy",
        frame_number=20,
        timestamp_seconds=0.66,
        label="motion_score",
        confidence=0.77,
        metadata={"mean_diff": 18.4, "max_diff": 120},
    )
```

## Database Fields

The `detections` table has these fields:

- `id`: auto-incrementing row id.
- `source`: video file, webcam, CCTV source, or user-defined source string.
- `framework`: one of `yolo`, `opencv`, `numpy`, or `custom`.
- `frame_number`: video frame number, nullable.
- `timestamp_seconds`: timestamp inside the video, nullable.
- `label`: detected label or result name.
- `confidence`: confidence score, nullable.
- `x1`, `y1`, `x2`, `y2`: bounding box coordinates, nullable.
- `width`, `height`: calculated from `bbox` when provided.
- `metadata_json`: JSON string for extra data, nullable.
- `created_at`: UTC ISO timestamp string.

## Managing The Library

For direct copy usage, treat `videoeventsql/` as the library folder. Keep its public API stable:

```python
from videoeventsql import VideoEventLogger
```

For v0.1, keep changes narrow:

- keep runtime code in `videoeventsql/__init__.py`
- do not add external dependencies
- do not add YOLO, OpenCV, or NumPy processing code
- do not add dashboards, APIs, CLI commands, or cloud features
- keep generated SQLite files out of git

If the project grows beyond one class and one table, split the code into separate modules later.

## Testing This Repository

From this repository root:

```bash
cd /path/to/videoevent-sql
python3 --version
python3 -m unittest discover
```

Expected result:

```text
Ran 8 tests
OK
```

## Testing Direct Copy Usage

Create a temporary project and copy only `videoeventsql/` into it:

```bash
mkdir -p /tmp/my-project
cp -R /path/to/videoevent-sql/videoeventsql /tmp/my-project/
cd /tmp/my-project
```

Create `main.py`:

```python
from videoeventsql import VideoEventLogger

with VideoEventLogger("events.db") as logger:
    row_id = logger.log_detection(
        source="sample.mp4",
        framework="yolo",
        label="person",
        bbox=[100, 80, 320, 460],
    )

print(row_id)
```

Run it:

```bash
python3 main.py
```

If it prints a row id and creates `events.db`, the copied folder works.

## Example Files

This repository includes examples:

```bash
python3 examples/yolo_result_example.py
python3 examples/opencv_result_example.py
python3 examples/numpy_result_example.py
```

Each example writes one row to `events.db`.

## Contributing

This is an open-source project. Anyone can contribute by opening issues, suggesting improvements, improving documentation, adding tests, or submitting pull requests.

Please keep the v0.1 scope small: VideoEventSQL should store already-generated results, not run YOLO, OpenCV, NumPy, web servers, dashboards, or cloud services.
