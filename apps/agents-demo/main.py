import json, datetime as dt
from agent import run_agent

if __name__ == "__main__":
    prompt = "Post 'Hello from the mock GrowthOps Agent!' to #general."
    result = run_agent(prompt)
    print("\n=== FINAL ANSWER ===\n", result["final_text"])
    print("\n=== TRACE (summary) ===")
    for step in result["trace"]["steps"]:
        print("-", step["type"])
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(f"../../logs/mock-agent-{ts}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nTrace written to logs/mock-agent-{ts}.json")
