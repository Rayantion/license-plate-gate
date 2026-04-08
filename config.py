# License Plate Recognition Configuration

# ==================
# DATABASE SETTINGS
# ==================
# Choose data source: "csv", "google_sheets", or "api"
DATA_SOURCE = "google_sheets"  # Using Google Sheets

# Google Sheets (if using DATA_SOURCE = "google_sheets")
SHEET_ID = "1VIAztguGHNYrQDWzkVjCGVAdkprd8BmBfH4hACuD3Ck"  # Get from your Google Sheet URL
# URL looks like: https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
SHEET_RANGE = "Sheet1!A:B"  # Column A = Plate, Column B = Owner

# API (if using DATA_SOURCE = "api")
API_URL = ""  # e.g., "https://your-api.com/check-plate"

# ================
# CAMERA SETTINGS
# ================
CAMERA_INDEX = 0  # 0 for default webcam
FRAME_WIDTH = 320  # Lower = faster (less processing)
FRAME_HEIGHT = 240  # Lower = faster

# ====================
# PLATE DETECTION
# ====================
# Taiwan plate dimensions (approximate)
# Reduced minimums for phone screen detection
MIN_PLATE_WIDTH = 40   # Was 80 - phone screens show smaller plates
MIN_PLATE_HEIGHT = 15  # Was 25 - phone screens show smaller plates
MAX_PLATE_WIDTH = 400
MAX_PLATE_HEIGHT = 150
ASPECT_RATIO_MIN = 1.5  # Was 2.0 - more lenient for phone angles
ASPECT_RATIO_MAX = 6.0  # Was 5.5 - more lenient
PLATE_REGION_PADDING = 10

# OCR settings
OCR_CONFIDENCE_THRESHOLD = 0.25

# Database settings
DATABASE_FILE = "allowed_plates.csv"

# Gate control (Optional - for Raspberry Pi)
USE_RELAY = False
RELAY_PIN = 18
RELAY_DURATION = 2

# Display settings
SHOW_DEBUG = True
FONT_SCALE = 0.7
BOX_THICKNESS = 2
TEXT_THICKNESS = 1

# Timing settings
CHECK_COOLDOWN = 2  # seconds between plate reads (reduced from 3 for faster response)
GATE_OPEN_DURATION = 5

# Frame skip settings (reduce lag by skipping OCR on some frames)
SKIP_FRAMES = 1  # Process every frame (was 2=every other frame)

# ==================
# TAIWAN PLATE FORMAT
# ==================
# Taiwan plates: AB-1234, ABC-1234, 1234-AB, etc.
TAIWAN_PLATE_REGEX = r'^[A-Z]{1,3}[-\s]?[0-9]{3,4}$'

# Common Taiwan plate patterns
# 51A-1234, 52A-1234 (普通小型車)
# 123-ABC (機車)
# AB-1234 (舊式)