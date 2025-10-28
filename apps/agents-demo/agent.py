import json, datetime as dt, time

def run_agent(user_prompt: str) -> dict:
    trace = {"start": dt.datetime.now().isoformat(), "steps": [], "mode": "offline-sim"}
    trace["steps"].append({"type": "model_decision",
                           "message": {"content": f"Pretend model understood prompt: '{user_prompt}'"}})
    time.sleep(0.4)
    fake_result = f"Would have posted '{user_prompt}' to #general"
    trace["steps"].append({"type": "tool_results",
                           "results": [{"name": "post_to_slack",
                                        "args": {"channel": "#general", "message": user_prompt},
                                        "result": fake_result}]})
    final_text = f"[MOCK RESPONSE] {fake_result}"
    trace["end"] = dt.datetime.now().isoformat()
    return {"final_text": final_text, "trace": trace}
