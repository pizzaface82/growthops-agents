import os
from pathlib import Path
import datetime as dt
import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="GrowthOps Agents", layout="wide")
st.title("GrowthOps Control Hub 🚀")

# Repo root discovery (so later we can import agents or load .env if needed)
REPO_ROOT = Path(__file__).resolve().parents[2]

# -----------------------------
# Sidebar (global controls)
# -----------------------------
with st.sidebar:
    st.header("Global Controls")
    st.caption("This dashboard will orchestrate your agents.")

    # Simple health checks
    venv_active = os.environ.get("VIRTUAL_ENV") or ""
    st.checkbox("Virtual env active", value=bool(venv_active), disabled=True)

    reqs_ok = Path(REPO_ROOT / "requirements.txt").exists()
    st.checkbox("requirements.txt found", value=reqs_ok, disabled=True)

    st.divider()
    st.caption("Tip: keep secrets in a .env at the repo root and NEVER commit it.")

# -----------------------------
# Tabs
# -----------------------------
tabs = st.tabs(["Overview", "SEO Agent", "Shopify Agent", "Paid Ops Agent", "Agent Logs"])

# ---- Overview
with tabs[0]:
    st.subheader("Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Connected Agents", 0)          # will increment as you add agents
    c2.metric("Last Run", "—")
    c3.metric("Status", "Idle")

    st.write(
        """
        This Control Hub is the front-end. In **Phase 1B**, you'll build a minimal OpenAI Agent with a Slack Action.
        In **Phase 1C**, you’ll wire a button here to trigger that Agent and show its result in *Agent Logs*.
        """
    )

# ---- SEO Agent
with tabs[1]:
    st.subheader("SEO Agent (prototype soon)")
    st.info("Coming soon: keyword clustering, SERP change detection, traffic insights.")
    st.write("For now, this is a placeholder panel where we’ll add inputs, uploads, and visualizations.")

# ---- Shopify Agent
with tabs[2]:
    st.subheader("Shopify Agent (prototype soon)")
    st.info("Coming soon: inventory sync, feed updates, and automation workflows.")

# ---- Paid Ops Agent
with tabs[3]:
    st.subheader("Paid Ops Agent (prototype soon)")
    st.info("Coming soon: budget allocator, performance alerts, and pacing checks.")

# ---- Agent Logs
with tabs[4]:
    st.subheader("Agent Logs")
    st.caption("When you connect the agent in Phase 1C, results and traces will show here.")
    if "agent_log" not in st.session_state:
        st.session_state.agent_log = []

    # Simple viewer for any logs we append later
    if st.session_state.agent_log:
        for i, entry in enumerate(reversed(st.session_state.agent_log), 1):
            with st.expander(f"Run {i} • {entry.get('ts','')}"):
                st.write(entry.get("message", ""))
    else:
        st.code("No agent runs yet. Finish Phase 1B and 1C to see output here.", language="markdown")

    # Dev helper: simulate a log entry (remove later)
    if st.button("Simulate Log Entry (dev only)"):
        st.session_state.agent_log.append({
            "ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "This is a placeholder log entry. Real results will appear after Phase 1C."
        })
        st.success("Added a demo log entry. Expand above to view.")
