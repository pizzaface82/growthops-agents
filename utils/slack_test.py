import os, json
from dotenv import load_dotenv

load_dotenv()
webhook = os.getenv("SLACK_WEBHOOK_URL", "mock://no-slack")

payload = {"text": "✅ GrowthOps Slack webhook test successful!"}

print("Webhook URL:", webhook)
print("Payload:", json.dumps(payload, indent=2))
print("✅ Dry-run successful (no Slack webhook used)")
