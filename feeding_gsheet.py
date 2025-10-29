import os
import sys
from dotenv import load_dotenv
import pytz
import pandas as pd
import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from requests.utils import quote
from debug_util import debug, debug_df
from debug_config import verbose

# Only load .env if running outside GitHub Actions
if os.path.exists(".env"):
    load_dotenv(dotenv_path=".env")
    debug("✅ Loaded .env from local file")
else:
    debug("📡 Skipping .env load (GitHub Action mode)")

env = os.environ.get("ENV_NAME", "Unknown")
if env == "Unknown":
    debug("❌ ENV_NAME not found in environment. Aborting script.")
    sys.exit(1)

else:
    debug(f"🌿 Running in {env.upper()} mode 🚀")

key_input = os.environ["KEY_FILE_NAME"]
bark_key = os.environ.get("BARK_KEY")

# 🧠 Determine whether this is a raw JSON string or a file path
if key_input.strip().startswith("{"):
    debug("🔐 Detected inlined JSON credentials from GitHub Secrets.")
    credentials_dict = json.loads(key_input)
else:
    debug(f"📄 Loading credentials from file: {key_input}")
    with open(key_input) as f:
        credentials_dict = json.load(f)

# Auth + config
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)

feeding_tracker = os.environ["FEEDING_TRACKER"]

# Open the sheets
debug("🧪 FEEDING from .env:", feeding_tracker)
feeding_spreadsheet = client.open_by_url(feeding_tracker).sheet1
feeding_df = pd.DataFrame(feeding_spreadsheet.get_all_records())

# Convert Date column to datetime, coercing invalids
feeding_df["Date"] = pd.to_datetime(feeding_df["Date"], format="%d/%m/%Y", errors="coerce")

# Keep only up to the last valid date (drops trailing empty rows)
last_valid_idx = feeding_df["Date"].last_valid_index()
if last_valid_idx is not None:
    feeding_df = feeding_df.loc[:last_valid_idx]

debug_df(feeding_df)

# Map of starter names to their Gsheet column and feeding frequency (days)
STARTERS = {
    "师弟": {
        "column_name": "White Flour Starter",
        "frequency_days": 4
    },
    "师兄": {
        "column_name": "Rye Starter",
        "frequency_days": 7
    },
    "Kefir": {
        "column_name": "Kefir",
        "frequency_days": 30
    },
}

tz = pytz.timezone("Europe/London")
today = pd.Timestamp.now(tz).date()
debug(today)

debug(feeding_df["Date"].tail(1))
debug(feeding_df.tail(1))

for name, info in STARTERS.items():
    col = info["column_name"]
    freq = info["frequency_days"]

    # find last non-empty cell in that column
    nonempty = feeding_df[feeding_df[col] != ""]
    
    last_row = nonempty.tail(1)

    last_row = nonempty.tail(1)
    last_fed = pd.Timestamp(last_row["Date"].values[0]).tz_localize(tz)
    
    next_due = (last_fed + pd.Timedelta(days=freq)).date()

    debug(col, today, next_due, today > next_due)

    if today > next_due:
        days_passed = (today - next_due).days
        title = f"{name} needs feeding 🍞!"
        body = f"它已经等你 {days_passed} 天了)"
        icon = "https://github.com/solastatech/household-notion-cron/blob/63550ac77e5a6f1172c6ba5b89043724751d6d9c/new%20logo%20TGR.png?raw=true"
        url = f"https://api.day.app/{bark_key}/{quote(title)}/{quote(body)}?icon={icon}"
        requests.get(url)
        print(f"🔔 Sent Bark notification for {name}")
    else:
        print(f"✅ {name} OK until {next_due.date()}")

