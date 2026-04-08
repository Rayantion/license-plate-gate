# License Plate Recognition Gate System

Control a gate based on license plate recognition.

## Setup

```bash
pip install opencv-python easyocr numpy pandas
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | Main program - runs everything |
| `plate_detector.py` | Detects license plates from camera |
| `ocr_reader.py` | Reads text from plate images |
| `database.py` | Checks plates against CSV database |
| `allowed_plates.csv` | List of allowed license plates |
| `config.py` | Settings |
| `requirements.txt` | Dependencies |

## Usage

1. Edit `allowed_plates.csv` to add allowed vehicle plates
2. Run:
```bash
python main.py
```

3. The program will:
   - Show camera feed
   - Detect license plates
   - Read the plate number
   - Check if allowed
   - Show GREEN (allowed) or RED (denied)

## Hardware (Optional)

To control a real gate:
- Connect relay to Raspberry Pi GPIO pins
- Edit `config.py` to set `RELAY_PIN`
- The program will trigger the relay when allowed

## Notes

- Uses EasyOCR (free, works offline)
- Works best with clear license plates
- Good lighting improves accuracy
- Edit `config.py` to adjust detection settings