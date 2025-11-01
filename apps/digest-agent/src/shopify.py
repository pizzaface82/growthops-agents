import os, requests
from datetime import datetime, timedelta

BASE = f"https://{os.getenv('SHOPIFY_STORE_DOMAIN')}/admin/api/2025-07"
TOKEN = os.getenv("SHOPIFY_ADMIN_TOKEN")

def fetch_shopify_summary(days: int = 1) -> dict:
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")
    url = f"{BASE}/orders.json?status=any&created_at_min={since}"
    r = requests.get(url, headers={"X-Shopify-Access-Token": TOKEN}, timeout=60)
    r.raise_for_status()
    orders = r.json().get("orders", [])
    revenue = sum(float(o.get("current_total_price", 0)) for o in orders)
    count = len(orders)
    aov = revenue / count if count else 0.0
    return {"orders": count, "revenue": revenue, "aov": aov}
