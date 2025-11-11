from __future__ import annotations
import pandas as pd

def _first_existing(df: pd.DataFrame, candidates: list[str], default_name: str, fill=pd.NA) -> str:
    """
    Return the first existing column name from candidates. If none exist,
    create default_name with `fill` and return default_name.
    """
    for c in candidates:
        if c in df.columns:
            return c
    df[default_name] = fill
    return default_name

def _coerce_bool_to_int_if_needed(df: pd.DataFrame, col: str) -> None:
    """
    If df[col] is boolean dtype, coerce to int so True > False when sorting desc.
    Safe no-op if column not in df.
    """
    if col in df.columns:
        try:
            if pd.api.types.is_bool_dtype(df[col].dtype):
                df[col] = df[col].astype(int)
        except Exception:
            # Be permissive; if coercion fails we leave the column as-is.
            pass

def fallback_rules(
    overlap_df: pd.DataFrame | None,
    organic_only_df: pd.DataFrame | None,
    paid_only_df: pd.DataFrame | None
) -> str:
    """
    Build a lightweight Markdown recommendation summary when LLM/API mode
    is disabled. Uses safe column resolution so schema changes won't crash.
    """

    # ---- Choose columns safely for each table
    # Overlap
    if overlap_df is None:
        overlap_df = pd.DataFrame()
    ovr = overlap_df.copy()

    ovr_query = _first_existing(ovr, ["query", "query_gsc", "kw_norm_gsc", "kw_norm"], "query")
    ovr_kw    = _first_existing(ovr, ["keyword", "keyword_ads", "kw_norm_ads", "kw_norm"], "keyword")
    ovr_pot   = _first_existing(ovr, ["organic_potential", "ovr_pot"], "organic_potential", fill=0)
    ovr_cpc   = _first_existing(ovr, ["cpc", "cpc_ads", "ovr_cpc"], "cpc", fill=0)
    ovr_pos   = _first_existing(ovr, ["position", "position_gsc", "ovr_pos"], "position", fill=pd.NA)

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
    # Wasted spend: overlap with high CPC or high organic potential; prefer reduce_bid_flag if present
    rb = "reduce_bid_flag" if "reduce_bid_flag" in ovr.columns else ovr_pot
    _coerce_bool_to_int_if_needed(ovr, "reduce_bid_flag")

    # Assemble sort columns defensively (all are strings with column names)
    sort_cols: list[str] = [rb]
    for c in (ovr_cpc, ovr_pot):
        if isinstance(c, str) and c in ovr.columns:
            sort_cols.append(c)

    if not ovr.empty:
        wasted = (
            ovr.sort_values(
                sort_cols,
                ascending=[False] * len(sort_cols),
                na_position="last"
            )
            .head(5)
        )
    else:
        wasted = ovr  # empty

    # Gaps to bid: organic-only with biggest impressions
    if not org.empty:
        gaps = org.sort_values(org_impr, ascending=False, na_position="last").head(5)
    else:
        gaps = org  # empty

    # ---- Markdown
    lines: list[str] = []

    # Wasted
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

    # Gaps
    lines.append("\n**Top 5 gaps to bid on**")
    if gaps.empty:
        lines.append("- No organic-only gaps detected this run.")
    else:
        for _, r in gaps.iterrows():
            q = r.get(org_query) or "n/a"
            imp = r.get(org_impr, 0)
            lines.append(f"- `{q}` — ~{imp} impressions and no paid coverage. Test exact/phrase.")

    # Actions
    lines.append("\n**3 actions (next 7 days)**")
    lines.append("- Reduce bids 10–25% on overlap where CPC is high and organic ranks ≤3.")
    lines.append("- Launch ads for top organic-only queries (≥300 weekly impressions).")
    lines.append("- Track CTR vs expected CTR; fix ≥5-point deficits with titles/meta & sitelinks.")

    return "\n".join(lines)