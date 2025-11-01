import os
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from .summarizer import summarize
from .slack import post_to_slack

load_dotenv(find_dotenv(), override=True)

def run_digest():
    mock = os.getenv("MOCK_DATA", "false").lower() == "true"

    if mock:
        today = {"revenue": 18450, "purchases": 120, "users": 4200, "sessions": 5300}
        yday  = {"revenue": 17400, "purchases": 115, "users": 4000, "sessions": 4900}
        channels = pd.DataFrame({
            "channel": ["Paid Search","Organic Search","Email","Social"],
            "sessions":[2100,1600,900,700],
            "revenue":[9500,5500,2700,1750],
        })
        products = pd.DataFrame([
            {"channel":"Organic","product":"Classic Sneaker","revenue":2100,"cvr":0.032},
            {"channel":"Paid","product":"Luxe Boot","revenue":1800,"cvr":0.028},
            {"channel":"Email","product":"Comfort Slide","revenue":950,"cvr":0.036},
        ])
    else:
        # TODO: replace with real GA4 + Shopify fetches for today & yesterday + joins
        raise NotImplementedError("Wire real GA4/Shopify here after mock validation.")

    # deltas
    def pct(new, old): 
        return None if not old else (new - old) / old * 100
    deltas = {
        "revenue_pct": pct(today["revenue"], yday["revenue"]),
        "purchases_pct": pct(today["purchases"], yday["purchases"]),
        "users_pct": pct(today["users"], yday["users"]),
        "sessions_pct": pct(today["sessions"], yday["sessions"]),
    }

    # AI summary (uses canned text if no OPENAI_API_KEY)
    summary = summarize(
        ga4_today=today, ga4_yday=yday, 
        channels=channels, products=products
    )

    msg = f"""*GrowthOps Daily Digest*
Revenue: ${today['revenue']:,} ({deltas['revenue_pct']:.2f}% vs yday)
Purchases: {today['purchases']} ({deltas['purchases_pct']:.2f}%)
Users: {today['users']} ({deltas['users_pct']:.2f}%), Sessions: {today['sessions']} ({deltas['sessions_pct']:.2f}%)

Topline:
{summary}
"""
    if os.getenv("SLACK_WEBHOOK_URL"): 
        post_to_slack(msg)

    return {
        "today": today, "yesterday": yday, "deltas": deltas,
        "channels": channels, "products": products,
        "summary": summary
    }
