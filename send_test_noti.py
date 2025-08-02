import sys
from dotenv import load_dotenv
import requests
from requests.utils import quote
import os

load_dotenv(dotenv_path=".env")
bark_key = os.environ.get("BARK_KEY")
print(bark_key)

# =======================================
# 🔔 Send Bark Notification
# =======================================
def send_bark_notification(title, body):
    icon = "https://raw.githubusercontent.com/solastatech/household-notion-cron/main/new%20logo%20TGR.png"
    url = f"https://api.day.app/{bark_key}/{quote(title)}/{quote(body)}?icon={icon}"
    r = requests.get(url)
    r.raise_for_status()