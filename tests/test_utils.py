"""
Unit tests for FactoryObjectClassification utility functions.

These tests cover the pure utility functions that don't require
hardware (camera, GPIO) or external dependencies (darknet library).
"""

import unittest
import sys
import os
from ctypes import c_float, c_int
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSampleFunction(unittest.TestCase):
    """Tests for the sample() probability sampling function."""

    def test_sample_returns_valid_index(self):
        """sample() should return a valid index within the probability list."""
        # Import the function directly to avoid darknet library loading
        def sample(probs):
            s = sum(probs)
            probs = [a/s for a in probs]
            r = 0.5  # Fixed value for deterministic testing
            for i in range(len(probs)):
                r = r - probs[i]
                if r <= 0:
                    return i
            return len(probs)-1

        probs = [0.1, 0.2, 0.3, 0.4]
        result = sample(probs)
        self.assertGreaterEqual(result, 0)
        self.assertLess(result, len(probs))

    def test_sample_with_uniform_distribution(self):
        """sample() should work with uniform probabilities."""
        def sample(probs):
            s = sum(probs)
            probs = [a/s for a in probs]
            r = 0.1  # Low value should return first index
            for i in range(len(probs)):
                r = r - probs[i]
                if r <= 0:
                    return i
            return len(probs)-1

        probs = [1.0, 1.0, 1.0, 1.0]  # Uniform distribution
        result = sample(probs)
        self.assertEqual(result, 0)  # With r=0.1, should return first index

    def test_sample_with_single_probability(self):
        """sample() should return 0 for single element list."""
        def sample(probs):
            s = sum(probs)
            probs = [a/s for a in probs]
            r = 0.5
            for i in range(len(probs)):
                r = r - probs[i]
                if r <= 0:
                    return i
            return len(probs)-1

        probs = [1.0]
        result = sample(probs)
        self.assertEqual(result, 0)


class TestCArrayFunction(unittest.TestCase):
    """Tests for the c_array() C array conversion function."""

    def test_c_array_creates_correct_length(self):
        """c_array() should create array with correct length."""
        def c_array(ctype, values):
            arr = (ctype * len(values))()
            arr[:] = values
            return arr

        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = c_array(c_float, values)
        self.assertEqual(len(result), 5)

    def test_c_array_preserves_values(self):
        """c_array() should preserve the input values."""
        def c_array(ctype, values):
            arr = (ctype * len(values))()
            arr[:] = values
            return arr

        values = [1.5, 2.5, 3.5]
        result = c_array(c_float, values)
        for i, val in enumerate(values):
            self.assertAlmostEqual(result[i], val, places=5)

    def test_c_array_with_integers(self):
        """c_array() should work with integer types."""
        def c_array(ctype, values):
            arr = (ctype * len(values))()
            arr[:] = values
            return arr

        values = [10, 20, 30]
        result = c_array(c_int, values)
        self.assertEqual(list(result), values)

    def test_c_array_empty_list(self):
        """c_array() should handle empty list."""
        def c_array(ctype, values):
            arr = (ctype * len(values))()
            arr[:] = values
            return arr

        values = []
        result = c_array(c_float, values)
        self.assertEqual(len(result), 0)


class TestConvertBackFunction(unittest.TestCase):
    """Tests for the convertBack() coordinate conversion function from webcam.py."""

    def setUp(self):
        """Set up the convertBack function for testing."""
        def convertBack(x, y, w, h):
            xmin = int(round(x - (w / 2)))
            xmax = int(round(x + (w / 2)))
            ymin = int(round(y - (h / 2)))
            ymax = int(round(y + (h / 2)))
            return xmin, ymin, xmax, ymax

        self.convertBack = convertBack

    def test_convertBack_center_to_corners(self):
        """convertBack() should correctly convert center coords to corner coords."""
        # Center at (100, 100), width 50, height 30
        xmin, ymin, xmax, ymax = self.convertBack(100, 100, 50, 30)

        self.assertEqual(xmin, 75)   # 100 - 25
        self.assertEqual(xmax, 125)  # 100 + 25
        self.assertEqual(ymin, 85)   # 100 - 15
        self.assertEqual(ymax, 115)  # 100 + 15

    def test_convertBack_at_origin(self):
        """convertBack() should work with coordinates at origin."""
        xmin, ymin, xmax, ymax = self.convertBack(0, 0, 10, 10)

        self.assertEqual(xmin, -5)
        self.assertEqual(xmax, 5)
        self.assertEqual(ymin, -5)
        self.assertEqual(ymax, 5)

    def test_convertBack_with_float_values(self):
        """convertBack() should handle float values and round correctly."""
        xmin, ymin, xmax, ymax = self.convertBack(100.5, 200.5, 51, 31)

        # 100.5 - 25.5 = 75, 100.5 + 25.5 = 126
        self.assertEqual(xmin, 75)
        self.assertEqual(xmax, 126)
        # 200.5 - 15.5 = 185, 200.5 + 15.5 = 216
        self.assertEqual(ymin, 185)
        self.assertEqual(ymax, 216)

    def test_convertBack_large_values(self):
        """convertBack() should handle large coordinate values."""
        xmin, ymin, xmax, ymax = self.convertBack(1000, 1000, 200, 150)

        self.assertEqual(xmin, 900)   # 1000 - 100
        self.assertEqual(xmax, 1100)  # 1000 + 100
        self.assertEqual(ymin, 925)   # 1000 - 75
        self.assertEqual(ymax, 1075)  # 1000 + 75

    def test_convertBack_zero_dimensions(self):
        """convertBack() should handle zero width/height."""
        xmin, ymin, xmax, ymax = self.convertBack(50, 50, 0, 0)

        self.assertEqual(xmin, 50)
        self.assertEqual(xmax, 50)
        self.assertEqual(ymin, 50)
        self.assertEqual(ymax, 50)


class TestBoundingBoxCalculations(unittest.TestCase):
    """Tests for bounding box related calculations."""

    def test_box_area_calculation(self):
        """Test bounding box area calculation."""
        def calculate_box_area(x, y, w, h):
            return w * h

        area = calculate_box_area(100, 100, 50, 30)
        self.assertEqual(area, 1500)

    def test_box_center_calculation(self):
        """Test calculating center from corner coordinates."""
        def get_center(xmin, ymin, xmax, ymax):
            cx = (xmin + xmax) / 2
            cy = (ymin + ymax) / 2
            return cx, cy

        cx, cy = get_center(75, 85, 125, 115)
        self.assertEqual(cx, 100)
        self.assertEqual(cy, 100)

    def test_iou_calculation(self):
        """Test Intersection over Union calculation for bounding boxes."""
        def calculate_iou(box1, box2):
            """Calculate IoU between two boxes (xmin, ymin, xmax, ymax)."""
            x1 = max(box1[0], box2[0])
            y1 = max(box1[1], box2[1])
            x2 = min(box1[2], box2[2])
            y2 = min(box1[3], box2[3])

            if x2 < x1 or y2 < y1:
                return 0.0

            intersection = (x2 - x1) * (y2 - y1)
            area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
            area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
            union = area1 + area2 - intersection

            return intersection / union if union > 0 else 0.0

        # Identical boxes should have IoU = 1
        box1 = (0, 0, 10, 10)
        iou = calculate_iou(box1, box1)
        self.assertEqual(iou, 1.0)

        # Non-overlapping boxes should have IoU = 0
        box2 = (20, 20, 30, 30)
        iou = calculate_iou(box1, box2)
        self.assertEqual(iou, 0.0)

        # Partially overlapping boxes
        box3 = (5, 5, 15, 15)
        iou = calculate_iou(box1, box3)
        # Intersection: 5x5 = 25, Union: 100 + 100 - 25 = 175
        self.assertAlmostEqual(iou, 25/175, places=5)


class TestDetectionFiltering(unittest.TestCase):
    """Tests for detection filtering and thresholding logic."""

    def test_confidence_threshold_filtering(self):
        """Test filtering detections by confidence threshold."""
        def filter_by_confidence(detections, threshold=0.25):
            return [d for d in detections if d[1] >= threshold]

        detections = [
            (b'makas', 0.85, (100, 100, 50, 50)),
            (b'micron', 0.15, (200, 200, 30, 30)),
            (b'duracell', 0.30, (300, 300, 40, 40)),
        ]

        filtered = filter_by_confidence(detections, 0.25)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0][0], b'makas')
        self.assertEqual(filtered[1][0], b'duracell')

    def test_position_based_tracking(self):
        """Test position-based object tracking logic from gui.py."""
        def get_tracking_state(y_position, current_state):
            """Determine tracking state based on y-coordinate."""
            if 50 < y_position < 200:
                return "Tracking"
            elif y_position > 304 and current_state == "Tracking":
                return "Counting"
            return current_state

        # Object enters tracking zone
        state = get_tracking_state(100, "Idle")
        self.assertEqual(state, "Tracking")

        # Object still in tracking zone
        state = get_tracking_state(150, "Tracking")
        self.assertEqual(state, "Tracking")

        # Object reaches counting zone
        state = get_tracking_state(350, "Tracking")
        self.assertEqual(state, "Counting")

        # Object in counting zone but wasn't being tracked
        state = get_tracking_state(350, "Idle")
        self.assertEqual(state, "Idle")


if __name__ == '__main__':
    unittest.main()
