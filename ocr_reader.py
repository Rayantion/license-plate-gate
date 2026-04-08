"""License Plate OCR Reader using EasyOCR"""

import cv2
import numpy as np
import easyocr
import config


# Initialize OCR reader (loads once, faster for subsequent reads)
# Using English and Vietnamese (common in Vietnam/Asia)
print("Loading OCR reader...")
reader = easyocr.Reader(['en', 'vi'], gpu=False)
print("OCR reader loaded!")


def preprocess_for_ocr(plate_image):
    """Preprocess plate image for better OCR results (PlateVision approach)"""
    # Convert to grayscale
    if len(plate_image.shape) == 3:
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = plate_image

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Apply Otsu's thresholding (automatic threshold selection)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh


def read_plate(plate_image):
    """Read text from license plate image"""
    try:
        # Convert image to numpy array if needed
        if not isinstance(plate_image, np.ndarray):
            return None

        # Preprocess
        processed = preprocess_for_ocr(plate_image)

        # Run OCR
        results = reader.readtext(processed)

        if not results:
            return None

        # Extract text from results
        plate_texts = []
        for detection in results:
            text = detection[1]
            confidence = detection[2]

            # Only include results with reasonable confidence
            if confidence > config.OCR_CONFIDENCE_THRESHOLD:
                # Clean up the text
                text = text.strip().upper()
                # Keep alphanumeric and common separators for Taiwan plates
                text = ''.join(c for c in text if c.isalnum() or c in '- ')
                if text:
                    plate_texts.append((text, confidence))

        if plate_texts:
            # Return the most confident result (not just longest)
            best = max(plate_texts, key=lambda x: x[1])
            return best[0]

        return None

    except Exception as e:
        print(f"OCR Error: {e}")
        return None


def normalize_plate(plate_text):
    """Normalize plate format (remove spaces, dashes, etc)"""
    if not plate_text:
        return None

    # Remove common separators
    plate_text = plate_text.replace(' ', '').replace('-', '').replace('.', '')

    # Convert to uppercase
    plate_text = plate_text.upper()

    return plate_text


def is_taiwan_plate_format(plate_text):
    """
    Validate if text matches Taiwan license plate format.
    More lenient validation - checks for plate-like patterns.
    """
    import re

    if not plate_text or len(plate_text) < 5 or len(plate_text) > 9:
        return False

    # Taiwan plates must have both letters AND digits
    has_letter = any(c.isalpha() for c in plate_text)
    has_digit = any(c.isdigit() for c in plate_text)
    if not (has_letter and has_digit):
        return False

    # Common Taiwan plate patterns (with or without separators):
    patterns = [
        # Standard formats with dash
        r'^[A-Z]{2}-\d{4}$',      # AB-1234 (old style)
        r'^\d{2}[A-Z]-\d{4}$',    # 51A-1234
        r'^\d{3}-[A-Z]{3}$',      # 123-ABC (motorcycle)
        r'^[A-Z]{3}-\d{4}$',      # ABC-1234 (special)
        r'^\d{4}-[A-Z]{2}$',      # 1234-AB (very old)
        # Without dash (normalized)
        r'^[A-Z]{2}\d{4}$',       # AB1234
        r'^\d{2}[A-Z]\d{4}$',     # 51A1234
        r'^\d{3}[A-Z]{3}$',       # 123ABC
        r'^[A-Z]{3}\d{4}$',       # ABC1234
        r'^\d{4}[A-Z]{2}$',       # 1234AB
    ]

    return any(re.match(p, plate_text) for p in patterns)