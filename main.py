import csv
import os
from datetime import datetime, timedelta

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from google.colab import files as colab_files
except ImportError:
    colab_files = None

if load_dotenv:
    load_dotenv()

CLIENT_ID = os.getenv("FIELDCLIMATE_CLIENT_ID")
CLIENT_SECRET = os.getenv("FIELDCLIMATE_CLIENT_SECRET")
USERNAME = os.getenv("FIELDCLIMATE_USERNAME")
PASSWORD = os.getenv("FIELDCLIMATE_PASSWORD")
DEVICE_ID = os.getenv("FIELDCLIMATE_DEVICE_ID")

# Get Unix timestamps for last 7 days
def get_unix_timestamps():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return int(start_date.timestamp()), int(end_date.timestamp())

# Get access token from FieldClimate API
def get_access_token():
    url = "https://oauth.fieldclimate.com/token"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Origin": "https://ng.fieldclimate.com",
    }
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json().get("access_token")

# Fetch daily data
def get_daily_data(access_token, start_unix, end_unix):
    url = f"https://api.fieldclimate.com/v2/fc/{DEVICE_ID}/daily/from/{start_unix}/to/{end_unix}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://ng.fieldclimate.com",
    }
    response = requests.post(url, headers=headers, json={})  # fetch all parameters
    if response.status_code != 200:
        print("Status:", response.status_code)
        print("Body:", response.text)
    response.raise_for_status()
    return response.json()

# Extract and prepare ET0 + Yağış [mm] data
def process_et0_data(full_data):
    grid_data = full_data['grid']['data']
    et0_precip_data = []

    for item in grid_data:
        dt = item['datetime']
        et0 = item.get('disease_evapotranspiration_ETo')
        precip = item.get('Yağış [mm]')
        et0_precip_data.append({
            'datetime': dt,
            'ET0_mm': et0,
            'Precipitation_mm': precip
        })

    return et0_precip_data

# Save data to CSV with totals
def save_to_csv(data):
    today_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"fieldclimate_et0_yagis_{today_str}.csv"

    total_et0 = 0.0
    total_precip = 0.0
    count = 0

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "ET0 (mm)", "Yağış (mm)"])

        for row in data:
            dt = row['datetime']
            et0 = row['ET0_mm']
            precip = row['Precipitation_mm']

            # Convert to float or 0
            et0_val = float(et0) if et0 is not None else 0.0
            precip_val = float(precip) if precip is not None else 0.0

            writer.writerow([dt, f"{et0_val:.2f}", f"{precip_val:.2f}"])

            total_et0 += et0_val
            total_precip += precip_val
            count += 1

        # Add totals row
        writer.writerow([])
        writer.writerow(["Weekly Total", f"{total_et0:.2f}", f"{total_precip:.2f}"])

    print(f"\nCSV saved as '{filename}'")
    if colab_files:
        colab_files.download(filename)
    else:
        print("Run in Google Colab to auto-download the CSV.")

# Main function
def main():
    try:
        missing = [
            name
            for name, value in {
                "FIELDCLIMATE_CLIENT_ID": CLIENT_ID,
                "FIELDCLIMATE_CLIENT_SECRET": CLIENT_SECRET,
                "FIELDCLIMATE_USERNAME": USERNAME,
                "FIELDCLIMATE_PASSWORD": PASSWORD,
                "FIELDCLIMATE_DEVICE_ID": DEVICE_ID,
            }.items()
            if not value
        ]
        if missing:
            missing_list = ", ".join(missing)
            raise ValueError(f"Missing required environment variables: {missing_list}")

        start_unix, end_unix = get_unix_timestamps()
        print("Authenticating...")
        access_token = get_access_token()

        print("Fetching daily data...")
        full_data = get_daily_data(access_token, start_unix, end_unix)

        print("Processing data...")
        et0_data = process_et0_data(full_data)

        print("Saving to CSV...")
        save_to_csv(et0_data)

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
    except KeyError as e:
        print(f"Missing expected field: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Run it
if __name__ == "__main__":
    main()
