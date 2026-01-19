# CLAUDE.md - Factory Object Classification

This document provides guidance for AI assistants working on this codebase.

## Project Overview

**Factory Object Classification** is a real-time object detection and counting system for factory automation. It detects and classifies factory objects (Duracell, Micron, Makas) on a conveyor belt using YOLO deep learning, displays results via a Kivy GUI, counts objects, and controls a stepper motor-driven conveyor belt via Raspberry Pi.

**Key workflow:**
1. Objects pass on a conveyor belt
2. Real-time detection/counting occurs when belt is running
3. Detection stops when belt stops
4. Data can be sent to cloud (Power BI) for analytics

## Repository Structure

```
FactoryObjectClassification/
├── gui.py              # Kivy GUI application (main entry point)
├── webcam.py           # Video capture and YOLO detection pipeline
├── darknet.py          # Darknet/YOLO Python wrapper (ctypes FFI)
├── step.py             # Stepper motor controller (Raspberry Pi)
├── data/
│   ├── obj.data        # YOLO configuration (3 classes, paths)
│   ├── obj.names       # Object class names: duracell, micron, makas
│   └── train.txt       # Training image paths
├── README.md           # High-level project documentation
└── LICENSE             # Apache 2.0 License
```

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3 |
| GUI Framework | Kivy |
| Computer Vision | OpenCV (cv2) |
| Deep Learning | YOLO (tiny), Darknet |
| Hardware Control | RPi.GPIO |
| IPC | UDP sockets |
| Concurrency | Threading |
| C Integration | ctypes |

## Key Components

### gui.py (Main Application)
- Kivy-based GUI with video display, counters, and control buttons
- Runs at 33 FPS using `Clock.schedule_interval(1.0/33.0)`
- Object tracking via Y-axis position (0-50px tracking start, >304px counting zone)
- Sends UDP "Start"/"Stop" commands to Raspberry Pi (192.168.1.32:8888)
- Saves detected object images to dataset directories
- Turkish UI labels: "BAŞLA" (Start), "DUR" (Stop), "Bant Durumu" (Belt Status)

### webcam.py (Detection Pipeline)
- Initializes video capture from default camera (`cv2.VideoCapture(0)`)
- Loads YOLO model and runs detection loop
- Detection threshold: 0.25
- Main function: `yolo()` generator returning (detections, frame) tuples
- `cvDrawBoxes()` for bounding box visualization

### darknet.py (YOLO Wrapper)
- Python wrapper around Darknet C library using ctypes
- Key structures: BOX, DETECTION, IMAGE, METADATA
- Main functions: `detect()`, `detect_image()`, `performDetect()`
- Platform support: Windows (DLL), Linux (.so)
- Uses global singletons: `netMain`, `metaMain`, `altNames`

### step.py (Hardware Control - Raspberry Pi)
- Stepper motor controller for conveyor belt
- GPIO pins: 13, 11, 15, 12 (BOARD numbering)
- UDP server on 0.0.0.0:8888
- Full-step 4-phase sequence with 0.03s step delay

## Entry Points

```bash
# Main GUI application
python3 gui.py

# Test detection loop (standalone)
python3 webcam.py

# Stepper motor control (Raspberry Pi only)
python3 step.py

# Test darknet detection on sample image
python3 darknet.py
```

## Code Conventions

### Naming
- Snake_case for functions and variables
- camelCase for some class methods
- Turkish labels in GUI elements

### Error Handling
- Try-except blocks used throughout
- Print statements for debugging (no formal logging)

### Threading
- Kivy Clock scheduler for frame updates (main thread)
- UDP listening in background thread (step.py)
- Main thread non-blocking on network I/O

### Video Processing Pipeline
```
capture frame → convert color space → resize → detect → draw boxes → texture update → GUI
```

## Hardcoded Configuration Values

| Parameter | Value | Location |
|-----------|-------|----------|
| RPi IP | 192.168.1.32 | gui.py |
| UDP Port | 8888 | gui.py, step.py |
| Detection Threshold | 0.25 | webcam.py |
| Detection Line Y | 304px | gui.py |
| Tracking Zone Y | 50-200px | gui.py |
| Stepper Delay | 0.03s | step.py |
| GPIO Pins | 13, 11, 15, 12 | step.py |
| Frame Rate | 33 FPS | gui.py |

**Note:** Model paths in webcam.py are hardcoded to `/home/alper/Desktop/darknet/...` - these need modification for different environments.

## Development Guidelines

### Making Changes

1. **GUI changes:** Modify `gui.py` - understand Kivy FloatLayout positioning
2. **Detection logic:** Modify `webcam.py` - adjust thresholds, frame processing
3. **Hardware control:** Modify `step.py` - GPIO sequencing, timing
4. **Model configuration:** Update paths in `webcam.py` or `data/obj.data`

### Common Tasks

**Adjust detection sensitivity:**
```python
# In webcam.py, modify thresh parameter in performDetect()
detections = performDetect(imagePath, thresh=0.25, ...)  # Lower = more sensitive
```

**Change counting zone:**
```python
# In gui.py, modify the Y-axis thresholds
if 0 < y1 < 50:  # Tracking start zone
if y1 > 304:      # Counting trigger line
```

**Modify GPIO pins:**
```python
# In step.py, modify pin assignments
PINS = [13, 11, 15, 12]  # BOARD numbering
```

## Dependencies

### Required
- `kivy` - GUI framework
- `opencv-python` (cv2) - Computer vision
- `numpy` - Numerical computing
- Compiled Darknet library (.dll/.so)
- Pre-trained YOLO weights

### Platform-Specific
- `RPi.GPIO` - Raspberry Pi GPIO control (RPi only)

### External Requirements
- YOLO configuration file (yolov3-tiny_obj.cfg)
- Pre-trained weights file (alper.weights)
- Camera connected to system

## Known Limitations

1. **Hardcoded paths:** Absolute paths to model files limit portability
2. **No configuration file:** All parameters hardcoded in source
3. **Limited error handling:** Bare except clauses may hide issues
4. **No test suite:** Manual testing required
5. **Turkish UI:** Interface labels in Turkish only
6. **Hardware dependent:** Requires camera, RPi, and stepper motor
7. **Single-user design:** No authentication or multi-user support

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│  PC (Detection System)                                  │
│  ┌─────────┐    ┌──────────┐    ┌─────────────────┐    │
│  │ Camera  │───▶│ webcam.py│───▶│ darknet.py     │    │
│  └─────────┘    │ (OpenCV) │    │ (YOLO detect)  │    │
│                 └──────────┘    └────────┬────────┘    │
│                                          │              │
│                 ┌────────────────────────▼──────────┐  │
│                 │        gui.py (Kivy)              │  │
│                 │  - Live video display             │  │
│                 │  - Object counts                  │  │
│                 │  - Start/Stop controls            │  │
│                 └──────────────┬────────────────────┘  │
│                                │ UDP                    │
└────────────────────────────────┼────────────────────────┘
                                 │ "Start"/"Stop"
                                 ▼
┌────────────────────────────────────────────────────────┐
│  Raspberry Pi                                          │
│  ┌──────────┐    ┌────────────────┐                   │
│  │ step.py  │───▶│ Stepper Motor  │───▶ Conveyor     │
│  │ (UDP Rx) │    │ (GPIO control) │                   │
│  └──────────┘    └────────────────┘                   │
└────────────────────────────────────────────────────────┘
```

## Object Classes

The system detects three object types defined in `data/obj.names`:
1. `duracell` - Battery
2. `micron` - Electronic component
3. `makas` - Scissors

## Testing Checklist

When making changes, verify:
- [ ] Camera feed displays correctly in GUI
- [ ] Objects are detected and bounded correctly
- [ ] Counting increments when objects cross detection line
- [ ] Start/Stop buttons send UDP commands
- [ ] Conveyor belt responds to commands (if hardware available)
- [ ] Detected images save to dataset directories

## Commit Message Guidelines

Follow the existing commit style:
- Short, descriptive messages
- Examples from history: "GUI Cleanup", "Stepper", "Step Script Added", "Counting Func Added"

---

# Code Quality Guidelines

## Refactoring Priorities

When improving this codebase, address issues in this order:

### Priority 1: Critical (Security & Stability)
| Issue | Location | Recommendation |
|-------|----------|----------------|
| Bare except clauses | All files | Replace with specific exceptions |
| No input validation | step.py UDP | Validate incoming commands |
| Hardcoded credentials/IPs | gui.py, webcam.py | Move to environment variables |

### Priority 2: High (Maintainability)
| Issue | Location | Recommendation |
|-------|----------|----------------|
| Hardcoded paths | webcam.py | Use config file or env vars |
| Global mutable state | darknet.py | Encapsulate in class |
| Magic numbers | gui.py (304, 50, 200) | Define as named constants |
| No logging | All files | Replace print with logging module |

### Priority 3: Medium (Code Quality)
| Issue | Location | Recommendation |
|-------|----------|----------------|
| Missing type hints | All files | Add type annotations |
| No docstrings | Most functions | Add documentation |
| Mixed naming conventions | All files | Standardize to snake_case |
| Code duplication | gui.py | Extract common patterns |

## Coding Standards

### Python Style Guide

```python
# Use snake_case for functions and variables
def calculate_detection_zone():
    detection_threshold = 0.25

# Use PascalCase for classes
class ConveyorController:
    pass

# Use UPPER_SNAKE_CASE for constants
DETECTION_THRESHOLD = 0.25
UDP_PORT = 8888
RPI_IP_ADDRESS = "192.168.1.32"
```

### Type Hints

```python
# Before (current code)
def cvDrawBoxes(detections, img):
    ...

# After (improved)
from typing import List, Tuple
import numpy as np

def cv_draw_boxes(
    detections: List[Tuple[str, float, Tuple[int, int, int, int]]],
    img: np.ndarray
) -> np.ndarray:
    ...
```

### Docstrings (Google Style)

```python
def perform_detect(
    image_path: str,
    thresh: float = 0.25,
    config_path: str = "./cfg/yolov3.cfg",
    weight_path: str = "./weights/yolov3.weights",
    meta_path: str = "./cfg/coco.data"
) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
    """Perform object detection on an image using YOLO.

    Args:
        image_path: Path to the input image file.
        thresh: Detection confidence threshold (0.0-1.0).
        config_path: Path to YOLO configuration file.
        weight_path: Path to pre-trained weights file.
        meta_path: Path to metadata file with class names.

    Returns:
        List of detections, each containing:
            - class_name: Detected object class
            - confidence: Detection confidence score
            - bbox: Bounding box as (x, y, width, height)

    Raises:
        FileNotFoundError: If model files are not found.
        RuntimeError: If detection fails.
    """
```

## Error Handling Patterns

### Current Anti-Pattern (Avoid)
```python
# BAD: Silent failure, hides bugs
try:
    detections = performDetect(...)
except:
    pass
```

### Recommended Pattern
```python
import logging

logger = logging.getLogger(__name__)

# GOOD: Specific exceptions with logging
try:
    detections = perform_detect(image_path, thresh=threshold)
except FileNotFoundError as e:
    logger.error(f"Model file not found: {e}")
    raise
except RuntimeError as e:
    logger.warning(f"Detection failed for frame, skipping: {e}")
    detections = []
except Exception as e:
    logger.exception(f"Unexpected error during detection: {e}")
    raise
```

### Exception Hierarchy for This Project
```python
class FactoryDetectionError(Exception):
    """Base exception for factory detection system."""
    pass

class ModelLoadError(FactoryDetectionError):
    """Raised when YOLO model fails to load."""
    pass

class CameraError(FactoryDetectionError):
    """Raised when camera capture fails."""
    pass

class CommunicationError(FactoryDetectionError):
    """Raised when UDP communication fails."""
    pass
```

## Logging Configuration

### Setup (add to main entry point)
```python
import logging
import sys
from datetime import datetime

def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                f"logs/factory_{datetime.now():%Y%m%d}.log"
            )
        ]
    )

# Usage in modules
logger = logging.getLogger(__name__)
logger.info("Detection started")
logger.debug(f"Frame processed: {frame_count}")
logger.warning(f"Low confidence detection: {confidence}")
logger.error(f"Failed to connect to RPi: {e}")
```

## Configuration Management

### Recommended: config.py
```python
"""Configuration management for Factory Object Classification."""
import os
from dataclasses import dataclass
from typing import Tuple

@dataclass
class NetworkConfig:
    rpi_ip: str = os.getenv("RPI_IP", "192.168.1.32")
    udp_port: int = int(os.getenv("UDP_PORT", "8888"))

@dataclass
class DetectionConfig:
    threshold: float = float(os.getenv("DETECTION_THRESHOLD", "0.25"))
    model_config: str = os.getenv("YOLO_CONFIG", "./cfg/yolov3-tiny_obj.cfg")
    model_weights: str = os.getenv("YOLO_WEIGHTS", "./weights/alper.weights")
    meta_path: str = os.getenv("YOLO_META", "./data/obj.data")

@dataclass
class GUIConfig:
    frame_rate: int = 33
    detection_line_y: int = 304
    tracking_zone_start: int = 0
    tracking_zone_end: int = 50
    window_size: Tuple[int, int] = (800, 600)

@dataclass
class GPIOConfig:
    pins: Tuple[int, ...] = (13, 11, 15, 12)
    step_delay: float = 0.03

# Global config instances
network = NetworkConfig()
detection = DetectionConfig()
gui = GUIConfig()
gpio = GPIOConfig()
```

### Environment Variables (.env example)
```bash
# Network
RPI_IP=192.168.1.32
UDP_PORT=8888

# Detection
DETECTION_THRESHOLD=0.25
YOLO_CONFIG=/path/to/yolov3-tiny_obj.cfg
YOLO_WEIGHTS=/path/to/alper.weights
YOLO_META=/path/to/obj.data

# Debug
LOG_LEVEL=INFO
```

## Security Considerations

### Input Validation
```python
# Validate UDP commands in step.py
VALID_COMMANDS = {"Start", "Stop"}

def handle_command(data: bytes) -> bool:
    """Validate and handle incoming UDP command."""
    try:
        command = data.decode("utf-8").strip()
        if command not in VALID_COMMANDS:
            logger.warning(f"Invalid command received: {command}")
            return False
        return process_command(command)
    except UnicodeDecodeError:
        logger.error("Received malformed data")
        return False
```

### Network Security
- Bind UDP server to specific interface, not 0.0.0.0
- Consider adding simple authentication token
- Validate source IP addresses

```python
# Improved UDP binding
ALLOWED_IPS = {"192.168.1.20"}  # PC IP

def start_udp_server(bind_ip: str = "192.168.1.32", port: int = 8888):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_ip, port))

    while True:
        data, addr = sock.recvfrom(1024)
        if addr[0] not in ALLOWED_IPS:
            logger.warning(f"Rejected connection from {addr[0]}")
            continue
        handle_command(data)
```

## Performance Optimization

### Detection Pipeline
```python
# Use frame skipping for better performance
class FrameProcessor:
    def __init__(self, skip_frames: int = 2):
        self.skip_frames = skip_frames
        self.frame_count = 0
        self.last_detections = []

    def process(self, frame: np.ndarray) -> List:
        self.frame_count += 1

        # Only run detection every N frames
        if self.frame_count % self.skip_frames == 0:
            self.last_detections = perform_detect(frame)

        return self.last_detections
```

### Memory Management
```python
# Release resources properly
class CameraCapture:
    def __init__(self, device: int = 0):
        self.cap = cv2.VideoCapture(device)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cap.release()
        cv2.destroyAllWindows()

    def read(self) -> Tuple[bool, np.ndarray]:
        return self.cap.read()

# Usage
with CameraCapture(0) as camera:
    ret, frame = camera.read()
```

## Testing Strategy

### Unit Test Structure
```
tests/
├── __init__.py
├── conftest.py          # pytest fixtures
├── test_darknet.py      # Detection wrapper tests
├── test_webcam.py       # Video capture tests
├── test_gui.py          # GUI component tests
├── test_step.py         # Stepper motor tests
└── mocks/
    ├── __init__.py
    ├── mock_camera.py   # Fake camera for testing
    └── mock_gpio.py     # Fake GPIO for non-RPi testing
```

### Example Test Cases
```python
# tests/test_detection.py
import pytest
from unittest.mock import Mock, patch

class TestDetection:
    def test_detection_returns_valid_format(self):
        """Detection should return list of (class, confidence, bbox)."""
        detections = perform_detect("test_image.jpg")

        assert isinstance(detections, list)
        for det in detections:
            class_name, confidence, bbox = det
            assert isinstance(class_name, str)
            assert 0.0 <= confidence <= 1.0
            assert len(bbox) == 4

    def test_detection_threshold_filtering(self):
        """Detections below threshold should be filtered."""
        low_thresh = perform_detect("test.jpg", thresh=0.1)
        high_thresh = perform_detect("test.jpg", thresh=0.9)

        assert len(low_thresh) >= len(high_thresh)

    @patch('webcam.cv2.VideoCapture')
    def test_camera_initialization(self, mock_capture):
        """Camera should initialize with correct device."""
        mock_capture.return_value.isOpened.return_value = True

        # Test camera init
        cap = initialize_camera(device=0)
        mock_capture.assert_called_with(0)
```

### Mock Objects
```python
# tests/mocks/mock_gpio.py
class MockGPIO:
    """Mock RPi.GPIO for testing on non-Raspberry Pi systems."""

    BOARD = 10
    OUT = 1
    IN = 0

    _pin_states = {}

    @classmethod
    def setmode(cls, mode):
        pass

    @classmethod
    def setup(cls, pin, mode):
        cls._pin_states[pin] = 0

    @classmethod
    def output(cls, pin, state):
        cls._pin_states[pin] = state

    @classmethod
    def cleanup(cls):
        cls._pin_states.clear()
```

## Code Smells to Watch For

| Smell | Example | Solution |
|-------|---------|----------|
| Long functions | `update()` in gui.py (50+ lines) | Extract into smaller methods |
| Deep nesting | Multiple if/try blocks | Use early returns, guard clauses |
| God class | ConnectPage does too much | Split into View and Controller |
| Feature envy | Accessing other object's data repeatedly | Move method to data owner |
| Primitive obsession | Passing x, y, w, h separately | Create BoundingBox dataclass |
| Duplicate code | Similar UDP send/receive patterns | Create network utility class |

## Recommended Tools

### Development
```bash
# Install development dependencies
pip install black isort flake8 mypy pytest pytest-cov

# Format code
black *.py
isort *.py

# Lint
flake8 *.py --max-line-length=100

# Type check
mypy *.py --ignore-missing-imports

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html
```

### Pre-commit Hook (.pre-commit-config.yaml)
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]
```

### pyproject.toml Configuration
```toml
[tool.black]
line-length = 100
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_ignores = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"
```

## Dependency Management

### requirements.txt (Production)
```
kivy>=2.0.0
opencv-python>=4.5.0
numpy>=1.19.0
```

### requirements-dev.txt (Development)
```
-r requirements.txt
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0
pytest>=7.0.0
pytest-cov>=4.0.0
pre-commit>=3.0.0
```

### requirements-rpi.txt (Raspberry Pi)
```
RPi.GPIO>=0.7.0
```

## Documentation Standards

### Module Header
```python
"""Factory Object Classification - GUI Module.

This module provides the Kivy-based graphical user interface for the
factory object classification system. It displays live camera feed,
detection results, object counts, and conveyor belt controls.

Typical usage:
    python gui.py

Attributes:
    FRAME_RATE (int): Target frames per second for GUI updates.
    DETECTION_LINE_Y (int): Y-coordinate for object counting trigger.
"""
```

### Inline Comments (when needed)
```python
# Only add comments for non-obvious logic
# BAD: increment counter by 1
count += 1

# GOOD: Reset tracking when object leaves detection zone
# to prevent double-counting on re-entry
if y_position > DETECTION_LINE_Y:
    self.tracking_state = "counted"
    self.active_track_id = None
```
