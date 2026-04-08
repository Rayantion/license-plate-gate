"""License Plate Recognition Gate Control System

Main program that runs the complete LPR gate system.
"""

import cv2
import time
import config
from plate_detector import get_plate_regions, draw_plate_boxes_with_status
from ocr_reader import read_plate, normalize_plate, is_taiwan_plate_format
from database import is_allowed_with_source, load_from_google_sheets, load_allowed_plates


# State variables
last_checked_plate = None
last_check_time = 0
current_status = "WAITING"  # WAITING, DETECTING, ALLOWED, DENIED, COOLDOWN
current_owner = ""
frame_count = 0


def process_plate(frame):
    """Process frame to detect and read license plates"""
    global last_checked_plate, last_check_time, current_status, current_owner, frame_count

    current_time = time.time()
    time_since_check = current_time - last_check_time
    frame_count += 1

    # Find potential plate regions
    plate_regions = get_plate_regions(frame)

    # No plates detected - reset status to WAITING
    if not plate_regions:
        current_status = "WAITING"
        return frame, None

    # Check if in cooldown period - still show DETECTING boxes but skip OCR
    if time_since_check < config.CHECK_COOLDOWN:
        current_status = "DETECTING"
        draw_plate_boxes_with_status(frame, plate_regions, "DETECTING")
        return frame, None

    # Frame skipping - only process every N frames to reduce lag
    if frame_count % config.SKIP_FRAMES != 0:
        current_status = "DETECTING"
        draw_plate_boxes_with_status(frame, plate_regions, "DETECTING")
        return frame, None

    # Try to read each plate region
    detected_plate = None
    valid_plate_region = None

    print(f"DEBUG: Found {len(plate_regions)} potential plate regions")
    for region in plate_regions:
        plate_image = region['image']
        plate_text = read_plate(plate_image)
        print(f"DEBUG: OCR result: {plate_text}")

        if plate_text:
            normalized = normalize_plate(plate_text)
            print(f"DEBUG: Normalized: {normalized}, Taiwan format: {is_taiwan_plate_format(normalized)}")
            # Validate Taiwan plate format
            if is_taiwan_plate_format(normalized):
                detected_plate = normalized
                valid_plate_region = region
                break

    if detected_plate:
        # Check database
        result = is_allowed_with_source(detected_plate)

        last_checked_plate = detected_plate
        last_check_time = current_time

        if result['allowed']:
            current_status = "ALLOWED"
            current_owner = result.get('owner', '')
            current_vehicle_type = result.get('vehicle_type', '')
            print(f"✅ ALLOWED: {detected_plate} ({current_owner}) - {current_vehicle_type}")
            # Draw GREEN box with owner and vehicle type
            owner_data = {'owner': current_owner, 'vehicle_type': current_vehicle_type}
            draw_plate_boxes_with_status(frame, [valid_plate_region], "ALLOWED", detected_plate, owner_data)
        else:
            current_status = "DENIED"
            current_owner = ""
            print(f"❌ DENIED: {detected_plate}")
            # Draw RED box
            draw_plate_boxes_with_status(frame, [valid_plate_region], "DENIED", detected_plate)
    else:
        # No valid Taiwan plate read after full OCR - show DETECTING boxes
        # User needs visual feedback that system is working
        current_status = "DETECTING"
        draw_plate_boxes_with_status(frame, plate_regions, "DETECTING")

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

    # Try DirectShow backend first (more reliable on Windows)
    cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)

    if not cap.isOpened():
        # Fallback to default backend
        cap = cv2.VideoCapture(config.CAMERA_INDEX)

    if not cap.isOpened():
        print("ERROR: Cannot open camera!")
        return

    # Optimize camera settings for lower latency
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

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
