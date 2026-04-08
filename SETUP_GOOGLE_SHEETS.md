# Google Sheets Setup Guide

## Step 1: Create Google Sheet

1. Go to https://sheets.google.com
2. Create a new sheet
3. Name it "License Plates"

## Step 2: Set Up Columns

In your sheet:
- **Column A**: Plate number (e.g., `51A-1234`)
- **Column B**: Owner name (optional, e.g., `John Doe`)

Example:
```
| Plate      | Owner          |
|------------|----------------|
| 51A-12345  | John Doe       |
| 52A-67890  | Admin Car      |
| 30A-88888  | VIP Vehicle    |
```

## Step 3: Get Sheet ID

1. In your browser URL bar, look at the sheet URL
2. The ID is between `/d/` and `/edit`
3. Example: `https://docs.google.com/spreadsheets/d/ABC123XYZ456/edit`
4. Your ID is: `ABC123XYZ456`

## Step 4: Get Google API Credentials

### Option A: Service Account (Recommended)

1. Go to https://console.cloud.google.com
2. Create a new project
3. Go to **APIs & Services** → **Library**
4. Enable **Google Sheets API**
5. Go to **APIs & Services** → **Credentials**
6. Click **Create Credentials** → **Service Account**
7. Fill in details and create
8. Download the JSON key file
9. Rename it to `credentials.json` and put in the project folder

### Option B: Share the Sheet

Simpler option (no API key needed):

1. In your Google Sheet, click **Share**
2. Add this email as editor:
   ```
   your-service-account@your-project.iam.gserviceaccount.com
   ```
3. Make sure the sheet is shared with "Anyone with link" OR share directly

## Step 5: Update Config

Edit `config.py`:
```python
DATA_SOURCE = "google_sheets"
SHEET_ID = "YOUR_SHEET_ID_HERE"  # From Step 3
```

## Step 6: Install Dependencies

```bash
pip install gspread google-auth
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| "credentials.json not found" | Download from Google Cloud Console |
| "Access denied" | Share the sheet with the service account email |
| "API not enabled" | Enable Google Sheets API in Cloud Console |

## Without Google API (Simple Version)

If you don't want to set up Google Cloud, just use the CSV file:

```python
DATA_SOURCE = "csv"  # Default
```

Edit `allowed_plates.csv` to add plates:
```
Plate,Owner
51A-12345,John
52A-67890,Admin
```