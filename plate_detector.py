"""License Plate Detection using OpenCV

Detects potential license plate regions in video frames.
"""

import cv2
import numpy as np
import config


def preprocess_image(frame):
    """Convert to grayscale and apply blur"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    return gray, blur


def find_plate_contours(blur_gray):
    """Find contours that might be license plates"""
    # Apply bilateral filter (better edge detection, less noise)
    bilateral = cv2.bilateralFilter(blur_gray, 11, 17, 17)

    # Edge detection
    edges = cv2.Canny(bilateral, 30, 200)

    # Find contours
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort by area and keep top 20 (like PlateVision)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20]

    return contours


def is_likely_plate(contour, frame_shape):
    """Check if contour is likely a license plate based on Taiwan plate characteristics"""
    x, y, w, h = cv2.boundingRect(contour)
    frame_area = frame_shape[0] * frame_shape[1]
    contour_area = cv2.contourArea(contour)

    # Check size constraints (relative to frame size)
    if w < config.MIN_PLATE_WIDTH or h < config.MIN_PLATE_HEIGHT:
        return False
    if w > config.MAX_PLATE_WIDTH or h > config.MAX_PLATE_HEIGHT:
        return False

    # Check aspect ratio (Taiwan plates are typically 2:1 to 5:1)
    aspect_ratio = w / h
    if aspect_ratio < config.ASPECT_RATIO_MIN or aspect_ratio > config.ASPECT_RATIO_MAX:
        return False

    # Check area - must be significant but not too large
    if contour_area < 500 or contour_area > frame_area * 0.3:
        return False

    # Check rectangularity (plates are roughly rectangular)
    perimeter = cv2.arcLength(contour, True)
    if perimeter > 0:
        approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
        # Plates should have 4 corners (quadrilateral) - like PlateVision
        if len(approx) != 4:
            return False

    return True


def get_plate_regions(frame):
    """Find all potential license plate regions"""
    gray, blur = preprocess_image(frame)
    contours = find_plate_contours(blur)

    plate_regions = []

    for contour in contours:
        if is_likely_plate(contour, frame.shape):
            x, y, w, h = cv2.boundingRect(contour)
            # Add padding
            pad = config.PLATE_REGION_PADDING
            x = max(0, x - pad)
            y = max(0, y - pad)
            w = min(frame.shape[1] - x, w + pad * 2)
            h = min(frame.shape[0] - y, h + pad * 2)

            # Crop the plate region
            plate_region = frame[y:y+h, x:x+w]
            plate_regions.append({
                'image': plate_region,
                'x': x,
                'y': y,
                'width': w,
                'height': h
            })

    return plate_regions


def draw_plate_boxes_with_status(frame, plate_regions, status, plate_text=None, owner=None):
    """
    Draw rectangles around detected plates with color-coded status.

    Args:
        frame: Video frame to draw on
        plate_regions: List of plate region dicts with x, y, width, height
        status: "DETECTING" (yellow), "ALLOWED" (green), "DENIED" (red)
        plate_text: Optional plate text to display
        owner: Optional owner name to display
    """
    output = frame.copy()

    # Status colors (BGR format)
    colors = {
        "DETECTING": ((0, 255, 255), (0, 200, 200), 2),  # Yellow
        "ALLOWED": ((0, 255, 0), (0, 200, 0), 4),         # Green
        "DENIED": ((0, 0, 255), (0, 0, 200), 4),          # Red
    }

    color, bg_color, thickness = colors.get(status, colors["DETECTING"])

    for region in plate_regions:
        x, y, w, h = region['x'], region['y'], region['width'], region['height']

        # Draw main box
        cv2.rectangle(output, (x, y), (x + w, y + h), color, thickness)

        # Draw glow effect
        cv2.rectangle(output, (x - 2, y - 2), (x + w + 2, y + h + 2), color, 1)
        cv2.rectangle(output, (x + 2, y + 2), (x + w - 2, y + h - 2), color, 1)

        # Draw label background
        label_y = y - 10 if y > 30 else y + h + 20
        label_height = 25
        cv2.rectangle(output, (x, label_y - label_height), (x + w, label_y), bg_color, -1)

        # Draw status text
        status_text = status
        if plate_text:
            status_text = f"{status}: {plate_text}"
            if owner:
                status_text = f"{plate_text} - {owner}"

        cv2.putText(output, status_text, (x + 5, label_y - 7),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return output


def draw_plate_boxes(frame, plate_regions):
    """Draw rectangles around detected plates (legacy function)"""
    return draw_plate_boxes_with_status(frame, plate_regions, "DETECTING")


def crop_plate_region(frame, x, y, w, h):
    """Crop a specific region as plate"""
    pad = 5
    x = max(0, x - pad)
    y = max(0, y - pad)
    w = min(frame.shape[1] - x, w + pad * 2)
    h = min(frame.shape[0] - y, h + pad * 2)
    return frame[y:y+h, x:x+w]
