import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import pytz
import json
from debug_util import debug, debug_df, debug_noti
from debug_config import verbose
from requests.utils import quote
from send_test_noti import send_bark_notification

load_dotenv(dotenv_path=".env")
env = os.environ.get("ENV_NAME", "Unknown")
if env == "Unknown":
    debug("❌ ENV_NAME not found in environment. Aborting script.")
    sys.exit(1)

else:
    debug(f"🌿 Running in {env.upper()} mode 🚀")

database_id = os.environ.get("DATABASE_ID")
notion_token = os.environ.get("NOTION_TOKEN")

if not database_id:
    debug(f"❌ DATABASE_ID not set. Please check your .env file or environment variables.")
    sys.exit(1)
else:
    debug(f"✅ DATABASE_ID loaded: {database_id[2]}")
    

# Map of starter names to their Notion column and feeding frequency (days)
STARTERS = {
    "师弟": {
        "column_name": "White Flour Starter",
        "frequency_days": 4
    },
    "师兄": {
        "column_name": "Rye Starter",
        "frequency_days": 7
    }
}

# =======================================
# 🧠 Function to query Notion database
# =======================================
def query_notion_database():
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()

data = query_notion_database()
if verbose:
    with open("notion_raw_dump.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent = 2)
        debug("✅ Dumped JSON to file.")

# =======================================
# 🧠 Parse latest feed dates per starter
# =======================================
def get_latest_feed_dates(notion_data):
    latest_dates = {name: None for name in STARTERS}
    for row in notion_data["results"]:
        props = row["properties"]
        date_str = props["Date"]["title"][0]["text"]["content"] if props["Date"]["title"] else None
        if not date_str:
            continue
        feed_date = datetime.strptime(date_str, "%d/%m/%Y")
        for starter, info in STARTERS.items():
            col_value = props.get(info["column_name"], {}).get("rich_text", [])
            if col_value and col_value[0]["plain_text"].strip():
                if latest_dates[starter] is None or feed_date > latest_dates[starter]:
                    latest_dates[starter] = feed_date
    return latest_dates

debug(get_latest_feed_dates(data))

# Debug Bark
debug_noti()

# =======================================
# 🏁 Main Logic
# =======================================
def main():
    notion_data = query_notion_database()
    latest_feeds = get_latest_feed_dates(notion_data)

    today = datetime.now(pytz.timezone("Europe/London")).date()
    overdue = []

    for starter, last_feed_date in latest_feeds.items():
        if last_feed_date is None:
            overdue.append(f"{starter} has **no recorded feedings**")
        else:
            days_passed = (today - last_feed_date.date()).days
            if days_passed >= STARTERS[starter]["frequency_days"]:
                overdue.append(f"{starter}已经等你{days_passed} 天了")

    if overdue:
        body = "\n".join(overdue)
        send_bark_notification("Feed Your Starters 🍞", body)
    else:
        print("All starters are up to date! 👨‍🌾")

main()







