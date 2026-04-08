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
    """Preprocess plate image for better OCR results"""
    # Convert to grayscale
    if len(plate_image.shape) == 3:
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = plate_image
    
    # Apply adaptive threshold
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    
    return denoised


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
                # Remove spaces and special chars (keep alphanumeric)
                text = ''.join(c for c in text if c.isalnum())
                if text:
                    plate_texts.append(text)
        
        if plate_texts:
            # Return the longest/most confident result
            return max(plate_texts, key=len)
        
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
    """Validate if text matches Taiwan license plate format"""
    import re

    if not plate_text:
        return False

    # Common Taiwan plate patterns:
    # AB-1234 (old style, 2 letters + 4 digits)
    # 51A-1234, 52A-1234 (3 chars: 2 digits + 1 letter + 4 digits)
    # 123-ABC (3 digits + 3 letters, common for motorcycles)
    # ABC-1234 (3 letters + 4 digits, special vehicles)
    # 1234-AB (4 digits + 2 letters, very old style)

    patterns = [
        r'^[A-Z]{2}\d{4}$',      # AB-1234 (old style)
        r'^\d{2}[A-Z]\d{4}$',    # 51A-1234
        r'^\d{3}[A-Z]{3}$',      # 123-ABC (motorcycle)
        r'^[A-Z]{3}\d{4}$',      # ABC-1234 (special)
        r'^\d{4}[A-Z]{2}$',      # 1234-AB (very old)
        r'^[A-Z]\d{2}[A-Z]\d{4}$',  # A12A-1234 (electric vehicles)
    ]

    return any(re.match(p, plate_text) for p in patterns)