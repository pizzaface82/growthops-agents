import os

PROPERTY_ID = os.getenv("GA4_PROPERTY_ID")

def fetch_ga4_summary(days: int = 1) -> dict:
    """
    Lazy-import the GA4 client so MOCK mode can run even if the GA4 package
    isn't installed or credentials aren't ready yet.
    """
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange, Metric, Dimension, RunReportRequest
    )

    client = BetaAnalyticsDataClient()  # uses GOOGLE_APPLICATION_CREDENTIALS
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        metrics=[
            Metric(name="totalUsers"),
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
        ],
        dimensions=[Dimension(name="date")],
    )
    resp = client.run_report(req)
    totals = {m.name: float(resp.totals[0].metric_values[i].value or 0)
              for i, m in enumerate(req.metrics)}
    return {
        "users": totals.get("totalUsers", 0),
        "active_users": totals.get("activeUsers", 0),
        "sessions": totals.get("sessions", 0),
        "purchases": totals.get("ecommercePurchases", 0),
        "revenue": totals.get("purchaseRevenue", 0.0),
    }
