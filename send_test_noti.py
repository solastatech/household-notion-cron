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
    icon = "https://github.com/solastatech/household-notion-cron/blob/63550ac77e5a6f1172c6ba5b89043724751d6d9c/new%20logo%20TGR.png?raw=true"
    url = f"https://api.day.app/{bark_key}/{quote(title)}/{quote(body)}?icon={icon}"
    r = requests.get(url)
    r.raise_for_status()