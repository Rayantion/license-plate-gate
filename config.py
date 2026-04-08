# License Plate Recognition Configuration

# ==================
# DATABASE SETTINGS
# ==================
# Choose data source: "csv", "google_sheets", or "api"
DATA_SOURCE = "csv"  # Change to "google_sheets" to use Google Sheets

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
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ====================
# PLATE DETECTION
# ====================
# Taiwan plate dimensions (approximate)
MIN_PLATE_WIDTH = 80
MIN_PLATE_HEIGHT = 25
MAX_PLATE_WIDTH = 400
MAX_PLATE_HEIGHT = 150
ASPECT_RATIO_MIN = 2.0
ASPECT_RATIO_MAX = 5.5
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
CHECK_COOLDOWN = 3  # seconds between same plate checks
GATE_OPEN_DURATION = 5

# ==================
# TAIWAN PLATE FORMAT
# ==================
# Taiwan plates: AB-1234, ABC-1234, 1234-AB, etc.
TAIWAN_PLATE_REGEX = r'^[A-Z]{1,3}[-\s]?[0-9]{3,4}$'

# Common Taiwan plate patterns
# 51A-1234, 52A-1234 (普通小型車)
# 123-ABC (機車)
# AB-1234 (舊式)