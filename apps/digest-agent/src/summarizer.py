import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

SYSTEM = """You are a marketing analyst. Compare today's KPIs to yesterday and explain
what changed and why. Output three sections:
1) Top 3 Wins, 2) Top 3 Risks, 3) 3 Recommended Actions.
Reference % changes and channels/products when relevant. Keep under 180 words."""

def summarize(ga4_today: dict, ga4_yday: dict, channels, products) -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    # Minimal text tables for the model:
    ch_txt = channels.to_string(index=False)
    pr_txt = products.to_string(index=False)
    content = (
        f"Today: {ga4_today}\nYesterday: {ga4_yday}\n\n"
        f"Channels:\n{ch_txt}\n\nTop Products by Channel:\n{pr_txt}"
    )

    if not key:
        # Mock summary if no key
        return (
            "Wins: Revenue +6.0% DoD; Paid drives most lift; Email CVR strong.\n"
            "Risks: Organic soft; sessions quality mixed; purchases up but CVR flat.\n"
            "Actions: +10% Paid retargeting; refresh top organic landing pages; test email promo."
        )

    from openai import OpenAI
    client = OpenAI(api_key=key)
    try:
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=content,
            instructions=SYSTEM,
        )
        return resp.output_text
    except TypeError:
        chat = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":SYSTEM},{"role":"user","content":content}],
        )
        return chat.choices[0].message.content
