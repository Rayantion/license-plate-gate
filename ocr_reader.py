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