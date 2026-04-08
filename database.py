"""License Plate Database with Google Sheets Support"""

import csv
import os
import json
import config

# Google Sheets credentials
CREDENTIALS_FILE = "credentials.json"


def load_from_google_sheets():
    """Load plates from Google Sheets"""
    try:
        import gspread
        from google.auth import credentials
        from google.oauth2 import service_account
        
        # Load credentials
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"Warning: {CREDENTIALS_FILE} not found")
            return None
        
        # Authorize
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        # Connect to sheet
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key(config.SHEET_ID).sheet1
        
        # Get all values
        data = sheet.get_all_values()
        
        # Parse plates (skip header row)
        plates = set()
        owners = {}
        
        for row in data[1:]:  # Skip header
            if row and len(row) > 0:
                plate = row[0].strip().upper().replace(' ', '').replace('-', '')
                if plate:
                    plates.add(plate)
                    if len(row) > 1:
                        owners[plate] = row[1]
        
        print(f"✅ Loaded {len(plates)} plates from Google Sheets")
        return {'plates': plates, 'owners': owners}
        
    except ImportError:
        print("Install gspread: pip install gspread google-auth")
        return None
    except Exception as e:
        print(f"Error loading from Google Sheets: {e}")
        return None


def check_plate_api(plate_text):
    """Check if plate is allowed via API"""
    import requests
    
    if not plate_text:
        return None
    
    normalized = plate_text.upper().replace(' ', '').replace('-', '')
    
    try:
        response = requests.post(
            config.API_URL,
            json={"plate": normalized},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'allowed': data.get('allowed', False),
                'owner': data.get('owner', ''),
                'vehicle_type': data.get('vehicle_type', '')
            }
    except Exception as e:
        print(f"API Error: {e}")
    
    return None


def load_allowed_plates():
    """Load allowed plates from local CSV"""
    plates = set()
    
    if not os.path.exists(config.DATABASE_FILE):
        print(f"Warning: {config.DATABASE_FILE} not found, creating empty database")
        create_sample_database()
    
    try:
        with open(config.DATABASE_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) > 0:
                    plate = row[0].strip().upper().replace(' ', '').replace('-', '')
                    if plate:
                        plates.add(plate)
    except Exception as e:
        print(f"Error loading database: {e}")
    
    return plates


def is_allowed(plate_text):
    """Check if a plate is in the allowed list"""
    if not plate_text:
        return False
    
    # Normalize the input plate
    normalized = plate_text.upper().replace(' ', '').replace('-', '')
    
    # Load current plates (local CSV)
    allowed_plates = load_allowed_plates()
    
    return normalized in allowed_plates


def is_allowed_with_source(plate_text):
    """Check plate and return details with source info"""
    if not plate_text:
        return {'allowed': False, 'source': 'none', 'owner': None}
    
    normalized = plate_text.upper().replace(' ', '').replace('-', '')
    
    # Option 1: Try Google Sheets first
    gs_data = load_from_google_sheets()
    if gs_data and normalized in gs_data['plates']:
        return {
            'allowed': True,
            'source': 'google_sheets',
            'owner': gs_data['owners'].get(normalized, '')
        }
    
    # Option 2: Check API if configured
    if hasattr(config, 'API_URL') and config.API_URL:
        api_result = check_plate_api(normalized)
        if api_result:
            return {
                'allowed': api_result['allowed'],
                'source': 'api',
                'owner': api_result.get('owner', '')
            }
    
    # Option 3: Fall back to local CSV
    allowed_plates = load_allowed_plates()
    return {
        'allowed': normalized in allowed_plates,
        'source': 'csv',
        'owner': None
    }


def add_plate(plate_text, owner_name=None):
    """Add a plate to the local CSV list"""
    if not plate_text:
        return False
    
    normalized = plate_text.upper().replace(' ', '').replace('-', '')
    
    try:
        with open(config.DATABASE_FILE, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if owner_name:
                writer.writerow([normalized, owner_name])
            else:
                writer.writerow([normalized])
        print(f"Added plate: {normalized}")
        return True
    except Exception as e:
        print(f"Error adding plate: {e}")
        return False


def remove_plate(plate_text):
    """Remove a plate from the allowed list"""
    if not plate_text:
        return False
    
    normalized = plate_text.upper().replace(' ', '').replace('-', '')
    plates = load_allowed_plates()
    
    if normalized in plates:
        plates.remove(normalized)
        try:
            with open(config.DATABASE_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for plate in plates:
                    writer.writerow([plate])
            print(f"Removed plate: {normalized}")
            return True
        except Exception as e:
            print(f"Error removing plate: {e}")
            return False
    
    return False


def create_sample_database():
    """Create a sample database with test plates"""
    sample_plates = [
        ['Plate', 'Owner'],
        ['51A-12345', 'Test Vehicle'],
        ['52A-67890', 'Admin Car'],
    ]
    
    try:
        with open(config.DATABASE_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for row in sample_plates:
                writer.writerow(row)
        print(f"Created sample database: {config.DATABASE_FILE}")
    except Exception as e:
        print(f"Error creating database: {e}")


def list_all_plates():
    """List all allowed plates"""
    return load_allowed_plates()


if __name__ == "__main__":
    # Test the database
    print("Testing database...")
    
    # Try Google Sheets
    print("\n--- Google Sheets ---")
    gs = load_from_google_sheets()
    if gs:
        print(f"Plates: {gs['plates']}")
        print(f"Owners: {gs['owners']}")
    
    # Try local CSV
    print("\n--- Local CSV ---")
    plates = list_all_plates()
    print(f"Allowed plates: {plates}")
    print(f"Is '51A-12345' allowed? {is_allowed('51A-12345')}")