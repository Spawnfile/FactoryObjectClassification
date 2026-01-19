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
