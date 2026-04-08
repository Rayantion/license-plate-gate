# License Plate Recognition Gate System

🚗 AI-powered Taiwan license plate recognition for access control using OpenCV + EasyOCR.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)

## Features

- ✅ **Real-time detection** from webcam/video feed
- ✅ **Taiwan plate validation** - prevents false positives from lights/signs
- ✅ **Google Sheets integration** - no credentials required (public API)
- ✅ **Color-coded feedback**:
  - 🟡 Yellow = Detecting/scanning
  - 🟢 Green = Allowed (shows owner + vehicle type)
  - 🔴 Red = Denied (not in database)
- ✅ **Optimized performance** - frame skipping + caching for smooth operation
- ✅ **Vehicle type display** - show car/motorcycle/truck from spreadsheet

## Quick Start

### Option 1: Download EXE (Windows)

1. Download `LicensePlateGate.exe` from [Releases](https://github.com/Rayantion/license-plate-gate/releases)
2. Run the executable
3. Point camera at license plate
4. System will auto-detect and check against database

### Option 2: Run from Source

```bash
# Install dependencies
pip install opencv-python easyocr numpy requests

# Run the system
python main.py
```

## Configuration

Edit `config.py` to customize:

```python
# Google Sheets (add your Sheet ID)
SHEET_ID = "your-sheet-id-here"

# Camera settings
FRAME_WIDTH = 320
FRAME_HEIGHT = 240

# Plate detection thresholds
MIN_PLATE_WIDTH = 40
MIN_PLATE_HEIGHT = 15
ASPECT_RATIO_MIN = 1.5
ASPECT_RATIO_MAX = 6.0

# Timing
CHECK_COOLDOWN = 2  # seconds between reads
SKIP_FRAMES = 3     # process every 3rd frame
```

## Google Sheets Setup

1. Create a Google Sheet with 3 columns:
   - **Column A**: Plate number (e.g., `51A-1234`)
   - **Column B**: Owner name (e.g., `John Doe`)
   - **Column C**: Vehicle type (e.g., `Car`, `Motorcycle`)

2. Make the sheet **public** (Anyone with link can view)

3. Copy the Sheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
                                    ^^^^^^^^^^^^^^^^^^^^^^^^
   ```

4. Paste into `config.py`

## Building from Source

```bash
# Install PyInstaller
pip install pyinstaller

# Build EXE
pyinstaller --onefile --name LicensePlateGate main.py

# EXE will be in dist/ folder
```

## Taiwan Plate Formats Supported

- `AB-1234` (old style)
- `51A-1234`, `52A-1234` (common modern)
- `123-ABC` (motorcycle)
- `ABC-1234` (special vehicles)
- `1234-AB` (very old style)
- `A12A-1234` (electric vehicles)

## Demo

![Demo](demo.png)

## Tech Stack

- **Python 3.8+**
- **OpenCV** - Computer vision
- **EasyOCR** - Text recognition
- **Google Sheets API** - Database (no auth required)

## License

MIT License - feel free to use and modify!
