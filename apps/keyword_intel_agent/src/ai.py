from __future__ import annotations
import pandas as pd

def _first_existing(df: pd.DataFrame, candidates: list[str], default_name: str, fill=pd.NA):
    for c in candidates:
        if c in df.columns:
            return c
    # create a safe default column if none exist
    df[default_name] = fill
    return default_name

def fallback_rules(overlap_df, organic_only_df, paid_only_df) -> str:
    # ---- Choose columns safely for each table
    # Overlap
    if overlap_df is None:
        overlap_df = pd.DataFrame()
    ovr = overlap_df.copy()
    ovr_query = _first_existing(ovr, ["query", "query_gsc", "kw_norm_gsc", "kw_norm"], "query")
    ovr_kw    = _first_existing(ovr, ["keyword", "keyword_ads", "kw_norm_ads", "kw_norm"], "keyword")
    ovr_pot   = _first_existing(ovr, ["organic_potential"], "organic_potential", fill=0)
    ovr_cpc   = _first_existing(ovr, ["cpc", "cpc_ads"], "cpc", fill=0)
    ovr_pos   = _first_existing(ovr, ["position", "position_gsc"], "position", fill=pd.NA)

    # Organic-only
    if organic_only_df is None:
        organic_only_df = pd.DataFrame()
    org = organic_only_df.copy()
    org_query = _first_existing(org, ["query", "query_gsc", "kw_norm_gsc", "kw_norm"], "query")
    org_impr  = _first_existing(org, ["impressions", "impressions_gsc"], "impressions", fill=0)

    # Paid-only (optional for future use)
    if paid_only_df is None:
        paid_only_df = pd.DataFrame()
    paid = paid_only_df.copy()
    paid_kw = _first_existing(paid, ["keyword", "keyword_ads", "kw_norm_ads", "kw_norm"], "keyword")

    # ---- Build lists
    # Wasted spend: overlap with high CPC or high organic potential
    wasted = ovr.sort_values([ovr_cpc, ovr_pot], ascending=[False, False]).head(5)

    # Gaps to bid: organic-only with biggest impressions
    gaps = org.sort_values(org_impr, ascending=False).head(5)

    lines = []
    lines.append("**Top 5 wasted spend**")
    if wasted.empty:
        lines.append("- No clear wasted spend detected this run.")
    else:
        for _, r in wasted.iterrows():
            q = r.get(ovr_query) or r.get(ovr_kw) or "n/a"
            cpc = r.get(ovr_cpc, 0)
            pot = r.get(ovr_pot, 0)
            pos = r.get(ovr_pos, "—")
            lines.append(f"- `{q}` — CPC ~{cpc}; organic potential {pot}; pos {pos}. Consider bid down/pause.")

    lines.append("\n**Top 5 gaps to bid on**")
    if gaps.empty:
        lines.append("- No organic-only gaps detected this run.")
    else:
        for _, r in gaps.iterrows():
            q = r.get(org_query) or "n/a"
            imp = r.get(org_impr, 0)
            lines.append(f"- `{q}` — ~{imp} impressions and no paid coverage. Test exact/phrase.")

    lines.append("\n**3 actions (7 days)**")
    lines.append("- Reduce bids 10–25% on overlap where CPC is high and organic ranks ≤3.")
    lines.append("- Launch ads for top organic-only queries (≥300 weekly impressions).")
    lines.append("- Track CTR vs expected CTR; fix ≥5-point deficits with titles/meta & sitelinks.")

    return "\n".join(lines)
