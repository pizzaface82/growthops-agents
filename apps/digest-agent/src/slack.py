import os, requests

def post_to_slack(text: str):
    url = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    if not url:
        # No webhook configured — just print and continue
        print("\n[Slack disabled] Message would be:\n", text)
        return
    r = requests.post(url, json={"text": text}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Slack webhook error {r.status_code}: {r.text[:300]}")
