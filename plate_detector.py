"""License Plate Detection using OpenCV"""

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
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    return contours


def is_likely_plate(contour):
    """Check if contour is likely a license plate"""
    x, y, w, h = cv2.boundingRect(contour)
    
    # Check size constraints
    if w < config.MIN_PLATE_WIDTH or h < config.MIN_PLATE_HEIGHT:
        return False
    if w > config.MAX_PLATE_WIDTH or h > config.MAX_PLATE_HEIGHT:
        return False
    
    # Check aspect ratio (license plates are typically 2:1 to 5:1)
    aspect_ratio = w / h
    if aspect_ratio < config.ASPECT_RATIO_MIN or aspect_ratio > config.ASPECT_RATIO_MAX:
        return False
    
    # Check area
    area = cv2.contourArea(contour)
    if area < 1000:
        return False
    
    return True


def get_plate_regions(frame):
    """Find all potential license plate regions"""
    gray, blur = preprocess_image(frame)
    contours = find_plate_contours(blur)
    
    plate_regions = []
    
    for contour in contours:
        if is_likely_plate(contour):
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


def draw_plate_boxes(frame, plate_regions):
    """Draw rectangles around detected plates"""
    output = frame.copy()
    
    for region in plate_regions:
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), config.BOX_THICKNESS)
    
    return output


def crop_plate_region(frame, x, y, w, h):
    """Crop a specific region as plate"""
    pad = 5
    x = max(0, x - pad)
    y = max(0, y - pad)
    w = min(frame.shape[1] - x, w + pad * 2)
    h = min(frame.shape[0] - y, h + pad * 2)
    return frame[y:y+h, x:x+w]