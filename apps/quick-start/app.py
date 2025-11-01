import os, sys, json, datetime as dt
from pathlib import Path
import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="GrowthOps Agents", layout="wide")
st.title("GrowthOps Control Hub 🚀")

# -----------------------------
# Paths
# -----------------------------
# repo root: .../growthops-agents/
REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_DEMO_DIR = REPO_ROOT / "apps" / "agents-demo"
LOGS_DIR = REPO_ROOT / "logs"

# Make sure we can import apps/agents-demo/agent.py
if str(AGENT_DEMO_DIR) not in sys.path:
    sys.path.append(str(AGENT_DEMO_DIR))

# Try to import the (mock) agent
run_agent = None
try:
    from agent import run_agent as _run_agent
    run_agent = _run_agent
except Exception as e:
    # we won't crash the UI; we'll show a message in the logs tab
    _agent_import_error = str(e)
else:
    _agent_import_error = None

# -----------------------------
# Sidebar (global controls)
# -----------------------------
with st.sidebar:
    st.header("Global Controls")
    st.caption("This dashboard triggers agents and shows their logs.")

    venv_active = os.environ.get("VIRTUAL_ENV") or ""
    st.checkbox("Virtual env active", value=bool(venv_active), disabled=True)
    st.checkbox("requirements.txt found", value=(REPO_ROOT / "requirements.txt").exists(), disabled=True)

    st.divider()
    st.caption("LOGS folder:")
    st.code(str(LOGS_DIR))

# -----------------------------
# Tabs
# -----------------------------
tabs = st.tabs(["Overview", "Run Agent", "Agent Logs"])

# ---- Overview
with tabs[0]:
    st.subheader("Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Connected Agents", 1 if run_agent else 0)
    c2.metric("Last Run", st.session_state.get("last_run", "—"))
    c3.metric("Status", "Ready" if run_agent else "Import error")

    st.write(
        """
        **Phase 1C:** Click **Run Agent** to execute the mock agent and write a JSON trace to `logs/`.
        Then open **Agent Logs** to view the latest run details.
        """
    )

# ---- Run Agent
with tabs[1]:
    st.subheader("Run Mock Agent")
    if _agent_import_error:
        st.error(f"Could not import agent from {AGENT_DEMO_DIR}:\n\n{_agent_import_error}")
    else:
        prompt = st.text_input(
            "Agent prompt",
            value="Post 'Hello from the mock GrowthOps Agent!' to #general."
        )

        run_col, spacer, _ = st.columns([1, 2, 2])
        with run_col:
            if st.button("▶️ Run Agent (mock)"):
                try:
                    res = run_agent(prompt)
                    # Save a JSON trace, just like main.py does
                    LOGS_DIR.mkdir(parents=True, exist_ok=True)
                    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
                    out_path = LOGS_DIR / f"mock-agent-{ts}.json"
                    with open(out_path, "w", encoding="utf-8") as f:
                        json.dump(res, f, indent=2)
                    st.session_state.last_run = ts
                    st.success(f"Agent run completed. Trace saved: {out_path.name}")
                    st.write("**Final Answer**")
                    st.code(res.get("final_text", ""), language="markdown")
                except Exception as e:
                    st.error(f"Agent run failed: {e}")

# ---- Agent Logs
with tabs[2]:
    st.subheader("Agent Logs")
    if not LOGS_DIR.exists():
        st.info("No logs directory yet. Run the agent first.")
    else:
        # Find recent JSON traces
        traces = sorted(LOGS_DIR.glob("mock-agent-*.json"), reverse=True)
        if not traces:
            st.info("No mock-agent JSON traces found yet. Click **Run Agent**.")
        else:
            # List the recent logs and show the selected one
            names = [p.name for p in traces]
            choice = st.selectbox("Select a trace to view", names, index=0)
            selected = LOGS_DIR / choice
            try:
                data = json.loads(selected.read_text(encoding="utf-8"))
            except Exception as e:
                st.error(f"Failed to read {choice}: {e}")
                data = None

            if data:
                st.markdown(f"**Trace file:** `{choice}`")
                # Summary
                meta_cols = st.columns(3)
                meta_cols[0].metric("Steps", len(data.get("trace", {}).get("steps", [])))
                meta_cols[1].metric("Mode", data.get("trace", {}).get("mode", "—"))
                meta_cols[2].metric("Started", data.get("trace", {}).get("start", "—"))

                st.divider()
                st.write("### Final Answer")
                st.code(data.get("final_text", ""), language="markdown")

                st.write("### Steps")
                for i, step in enumerate(data.get("trace", {}).get("steps", []), start=1):
                    with st.expander(f"Step {i}: {step.get('type','(unknown)')}"):
                        st.json(step)
