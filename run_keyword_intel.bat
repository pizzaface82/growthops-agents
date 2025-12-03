@echo off
set "PYTHONPATH=C:\Users\Eric\code\growthops-agents"
cd /d C:\Users\Eric\code\growthops-agents
"C:\Users\Eric\code\growthops-agents\.venv\Scripts\python.exe" -m apps.keyword_intel_agent.cli --gsc apps\keyword_intel_agent\data\sample_gsc.csv --ads apps\keyword_intel_agent\data\sample_ads.csv --out out\recommendations.md
