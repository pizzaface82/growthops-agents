import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

SYSTEM = """You are a concise marketing analyst.
Summarize metrics into: Top 3 Wins, Top 3 Risks, and 3 Actionable Recommendations.
Be specific, reference metrics, keep it under 180 words."""

def summarize(ga4: dict, shopify: dict) -> str:
    # MOCK mode: if no key, return canned text so you can run end-to-end without APIs
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return (
            "Top 3 Wins:\n"
            "• Revenue +5% DoD\n• AOV stable\n• Purchases steady\n\n"
            "Top 3 Risks:\n"
            "• Sessions down\n• New users flat\n• Conv. rate soft\n\n"
            "Recommended Actions:\n"
            "• +10% retargeting budget\n• QA top landing pages\n• Launch one promo test"
        )

    # Import on-demand so MOCK mode doesn't require the package
    from openai import OpenAI
    client = OpenAI(api_key=key)

    content = (
        f"GA4: users={ga4['users']}, active={ga4['active_users']}, "
        f"sessions={ga4['sessions']}, purchases={ga4['purchases']}, "
        f"revenue={ga4['revenue']}\n"
        f"Shopify: orders={shopify['orders']}, revenue={shopify['revenue']}, aov={shopify['aov']}"
    )

    # Try Responses API first (modern), fall back to Chat Completions if needed
    try:
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=content,
            instructions=SYSTEM,  # <— use 'instructions' (not 'system')
        )
        return resp.output_text
    except TypeError:
        # Older client – use Chat Completions
        chat = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": content},
            ],
        )
        return chat.choices[0].message.content
