"""License Plate Recognition Gate Control System

Main program that runs the complete LPR gate system.
"""

import cv2
import time
import config
from plate_detector import get_plate_regions, draw_plate_boxes
from ocr_reader import read_plate, normalize_plate
from database import is_allowed_with_source, load_from_google_sheets, load_allowed_plates


# State variables
last_checked_plate = None
last_check_time = 0
current_status = "WAITING"
display_text = "Scanning..."
current_owner = ""


def draw_status(frame, status, plate_text=None, owner=None):
    """Draw status overlay on frame"""
    output = frame.copy()
    height, width = output.shape[:2]
    
    # Status color
    if status == "ALLOWED":
        color = (0, 255, 0)  # Green
        bg_color = (0, 100, 0)
        text = f"ALLOWED: {plate_text}"
    elif status == "DENIED":
        color = (0, 0, 255)  # Red
        bg_color = (0, 0, 100)
        text = f"DENIED: {plate_text or 'Unknown'}"
    else:
        color = (255, 255, 0)  # Yellow
        bg_color = (100, 100, 0)
        text = "SCANNING..."
    
    # Draw status box
    cv2.rectangle(output, (0, height - 80), (width, height), bg_color, -1)
    cv2.rectangle(output, (0, height - 80), (width, height), color, 3)
    
    # Draw main status text
    cv2.putText(output, text, (20, height - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Draw owner if available
    if owner and status == "ALLOWED":
        cv2.putText(output, f"Owner: {owner}", (20, height - 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 200), 1)
    
    return output


def process_plate(frame):
    """Process frame to detect and read license plates"""
    global last_checked_plate, last_check_time, current_status, display_text, current_owner
    
    # Find potential plate regions
    plate_regions = get_plate_regions(frame)
    
    if not plate_regions:
        current_status = "WAITING"
        display_text = "Scanning..."
        return frame, None
    
    # Try to read each plate region
    detected_plate = None
    
    for region in plate_regions:
        plate_image = region['image']
        plate_text = read_plate(plate_image)
        
        if plate_text:
            normalized = normalize_plate(plate_text)
            # Taiwan plates are typically 4-7 chars
            if normalized and 4 <= len(normalized) <= 8:
                detected_plate = normalized
                break
    
    if detected_plate:
        current_time = time.time()
        
        # Check cooldown or new plate
        if last_checked_plate != detected_plate or \
           current_time - last_check_time > config.CHECK_COOLDOWN:
            
            # Check database
            result = is_allowed_with_source(detected_plate)
            
            last_checked_plate = detected_plate
            last_check_time = current_time
            
            if result['allowed']:
                current_status = "ALLOWED"
                display_text = f"ALLOWED: {detected_plate}"
                current_owner = result.get('owner', '')
                print(f"✅ ALLOWED: {detected_plate} ({current_owner})")
            else:
                current_status = "DENIED"
                display_text = f"DENIED: {detected_plate}"
                current_owner = ""
                print(f"❌ DENIED: {detected_plate}")
    
    # Draw debug boxes
    if config.SHOW_DEBUG and plate_regions:
        frame = draw_plate_boxes(frame, plate_regions)
    
    # Draw status
    frame = draw_status(frame, current_status, last_checked_plate, current_owner)
    
    return frame, detected_plate


def main():
    """Main loop"""
    print("=" * 50)
    print("License Plate Recognition Gate System")
    print("=" * 50)
    
    # Show database info
    print(f"\n📊 Data source: {config.DATA_SOURCE}")
    
    if config.DATA_SOURCE == "google_sheets":
        gs = load_from_google_sheets()
        if gs:
            print(f"Loaded {len(gs['plates'])} plates from Google Sheets")
    else:
        plates = load_allowed_plates()
        print(f"Loaded {len(plates)} plates from CSV")
    
    print("\n📷 Initializing camera...")
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    
    if not cap.isOpened():
        print("ERROR: Cannot open camera!")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    
    print(f"Camera ready! Resolution: {config.FRAME_WIDTH}x{config.FRAME_HEIGHT}")
    print("\nPress 'q' to quit")
    print("=" * 50)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Cannot read frame")
            break
        
        processed_frame, detected = process_plate(frame)
        
        cv2.imshow("License Gate Control", processed_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nQuitting...")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Done!")


if __name__ == "__main__":
    main()