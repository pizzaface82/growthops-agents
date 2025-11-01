from dotenv import load_dotenv, find_dotenv
# replace: load_dotenv()
load_dotenv(find_dotenv(), override=True)
import os
from dotenv import load_dotenv, find_dotenv
from .ga4 import fetch_ga4_summary
from .shopify import fetch_shopify_summary
from .summarizer import summarize
from .slack import post_to_slack

load_dotenv(find_dotenv(), override=True)

def run_digest() -> dict:
    if os.getenv("MOCK_DATA", "false").lower() == "true":
        ga4 = {"users": 4200, "active_users": 3100, "sessions": 5300, "purchases": 120, "revenue": 18450.0}
        shop = {"orders": 115, "revenue": 17980.0, "aov": 156.35}
    else:
        ga4 = fetch_ga4_summary(days=1)
        shop = fetch_shopify_summary(days=1)

    summary = summarize(ga4, shop)
    message = f"*GrowthOps Daily Digest*\n\n{summary}"
    if os.getenv("SLACK_WEBHOOK_URL"):
        post_to_slack(message)
    return {"ga4": ga4, "shopify": shop, "summary": summary}
