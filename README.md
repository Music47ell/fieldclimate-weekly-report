# FieldClimate ET0 + Precipitation Export

Fetches the last 7 days of daily data from the FieldClimate API for a single device, then writes a CSV containing ET0 and precipitation totals. Designed for quick weekly reporting.

## What it does
- Authenticates against the FieldClimate OAuth endpoint
- Requests daily data for the last 7 days for a single device
- Extracts ET0 (`disease_evapotranspiration_ETo`) and precipitation (`Yağış [mm]`)
- Writes a CSV with daily values and weekly totals
- Downloads the CSV automatically when run inside Google Colab

## Requirements
- Python 3.9+
- A FieldClimate account and API credentials
- A device ID for the station you want to query

## Setup
1. Create a virtual environment (optional but recommended)
2. Install dependencies
3. Configure environment variables

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```ini
FIELDCLIMATE_CLIENT_ID=your_client_id
FIELDCLIMATE_CLIENT_SECRET=your_client_secret
FIELDCLIMATE_USERNAME=your_username
FIELDCLIMATE_PASSWORD=your_password
FIELDCLIMATE_DEVICE_ID=your_device_id
```

## Run
```bash
python main.py
```

## Output
A CSV file named like `fieldclimate_et0_yagis_YYYY-MM-DD.csv` containing:
- Date
- ET0 (mm)
- Yağış (mm)
- Weekly totals row at the bottom

## Notes
- If you run this outside Google Colab, the CSV will be saved locally and a message will be printed instead of auto-download.
- The script expects the API response to contain `grid.data` with the keys listed above.

## Troubleshooting
- Missing credentials: ensure all `FIELDCLIMATE_*` variables are set in `.env`.
- 401/403: verify API credentials and device permissions.
