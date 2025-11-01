# 🧠 GrowthOps Agents

A collection of AI-powered marketing automation agents built with Python, Streamlit, and the OpenAI SDK.

Each agent connects real marketing data (GA4, Shopify, Slack, etc.) to actionable insights and automation flows.

---

## 🚀 Current Agents

### 1. GrowthOps Digest Agent

**Goal:** Automate your daily marketing performance summary
**Stack:** Python · Streamlit · OpenAI SDK · GA4 · Shopify · Slack
**Output:** “Top 3 Wins / 3 Risks / 3 Actions” via CLI or Streamlit dashboard

**Run locally:**

```bash
# activate virtual environment
.\.venv\Scripts\Activate.ps1

# run mock data (no API keys required)
python .\apps\digest-agent\main.py

# or run the dashboard
python -m streamlit run .\apps\digest-agent\app.py
```

---

## 🧩 Folder Structure

```
growthops-agents/
├── apps/
│   ├── digest-agent/
│   │   ├── src/
│   │   ├── main.py
│   │   ├── app.py
│   │   └── .env (excluded from git)
├── logs/
├── requirements.txt
└── README.md
```

---

## 💻 Stack

* Python 3.10+
* Streamlit
* OpenAI SDK
* Google Analytics Reporting API
* Shopify Admin API
* Slack Webhooks
* python-dotenv

---

## 🧠 Next Phase

**Phase 2 – Streamlit UI & Slack Integration**

* Add real GA4 + Shopify connections
* Add automated Slack digest posting
* Polish dashboard layout

**Phase 3 – Add next agent: “Marketing Performance Analyzer”**

---

📍 *Created by Eric Amzallag — Building GrowthOps AI Agents for E-Commerce*
