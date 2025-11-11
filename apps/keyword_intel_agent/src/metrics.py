from __future__ import annotations
import pandas as pd
from rapidfuzz import process, fuzz
from .normalize import normalize_kw


# -----------------------------------------------------------------------------
#  Expected CTR curve (for estimating organic potential)
# -----------------------------------------------------------------------------
def expected_ctr(position: float) -> float:
    if position <= 1: return 0.30
    if position <= 2: return 0.20
    if position <= 3: return 0.15
    if position <= 5: return 0.10
    if position <= 10: return 0.05
    return 0.02


# -----------------------------------------------------------------------------
#  Utility to add normalized keyword columns
# -----------------------------------------------------------------------------
def add_kw_norm_cols(gsc: pd.DataFrame, ads: pd.DataFrame):
    gsc = gsc.copy()
    ads = ads.copy()
    gsc["kw_norm"] = gsc["query"].map(normalize_kw)
    ads["kw_norm"] = ads["keyword"].map(normalize_kw)
    return gsc, ads


# -----------------------------------------------------------------------------
#  Compute overlaps (exact or fuzzy)
# -----------------------------------------------------------------------------
def compute_overlap_segments(gsc: pd.DataFrame, ads: pd.DataFrame, fuzzy=False, threshold=90):
    """Return dict with overlap, organic_only, paid_only DataFrames."""
    if not fuzzy:
        merged = pd.merge(
            gsc, ads,
            on="kw_norm", how="outer",
            suffixes=("_gsc", "_ads"),
            indicator=True
        )
    else:
        # Safe suffixing avoids duplicate columns
        g = gsc.copy().add_suffix("_gsc")
        a = ads.copy().add_suffix("_ads")

        # Fuzzy map
        left = g["kw_norm_gsc"].drop_duplicates().tolist()
        right = a["kw_norm_ads"].drop_duplicates().tolist()
        pairs = []
        for kw in left:
            match = process.extractOne(kw, right, scorer=fuzz.token_sort_ratio)
            if match and match[1] >= threshold:
                pairs.append((kw, match[0]))
        map_df = pd.DataFrame(pairs, columns=["kw_norm_gsc", "kw_norm_ads"])

        merged = g.merge(map_df, on="kw_norm_gsc", how="left")
        merged = merged.merge(a, on="kw_norm_ads", how="outer", indicator=True)
        merged["kw_norm"] = merged["kw_norm_gsc"].fillna(merged["kw_norm_ads"])

    overlap = merged[merged["_merge"] == "both"].copy()
    organic_only = merged[merged["_merge"] == "left_only"].copy()
    paid_only = merged[merged["_merge"] == "right_only"].copy()
    return {"overlap": overlap, "organic_only": organic_only, "paid_only": paid_only}


# -----------------------------------------------------------------------------
#  Compute ROI signals, CTR gaps, and priority scores
# -----------------------------------------------------------------------------
def roi_signals(overlap: pd.DataFrame) -> pd.DataFrame:
    df = overlap.copy()

    # Canonicalize columns regardless of merge path
    alias_map = [
        ("position",    ["position", "position_gsc"]),
        ("ctr",         ["ctr", "ctr_gsc"]),
        ("impressions", ["impressions", "impressions_gsc"]),
        ("cpc",         ["cpc", "cpc_ads"]),
        ("cost",        ["cost", "cost_ads"]),
        ("conversions", ["conversions", "conversions_ads"]),
        ("query",       ["query", "query_gsc", "kw_norm_gsc", "kw_norm"]),
        ("keyword",     ["keyword", "keyword_ads", "kw_norm_ads", "kw_norm"]),
        ("clicks_gsc",  ["clicks_gsc", "clicks_x", "clicks"]),
        ("clicks_ads",  ["clicks_ads", "clicks_y"]),
    ]
    for target, cands in alias_map:
        if target not in df.columns:
            for c in cands:
                if c in df.columns:
                    df[target] = df[c]
                    break

    for col in ["position", "ctr", "impressions"]:
        if col not in df.columns:
            df[col] = pd.NA

    # Expected CTR & gaps
    df["expected_ctr"] = df["position"].astype(float).map(expected_ctr)
    df["ctr_gap"] = (df["expected_ctr"] - df["ctr"].astype(float)).round(4)

    # Organic potential
    df["organic_potential"] = (df["impressions"].astype(float) * df["ctr_gap"].clip(lower=0)).round(2)

    # Wasted spend flags
    df["high_cpc_flag"] = ((df.get("cpc", 0).astype(float) > 2.5) & (df["organic_potential"] > 20)).astype(int)
    df["reduce_bid_flag"] = ((df["position"].astype(float) <= 3.0) & (df.get("cpc", 0).astype(float) > 0)).astype(int)

    # Priority score
    df["priority"] = (
        df["organic_potential"].rank(ascending=False, method="first").fillna(0) +
        (df["high_cpc_flag"] * 2) +
        (df["reduce_bid_flag"] * 1)
    ).astype(float)

    # Preferred display order
    preferred = [
        "page","query","keyword","kw_norm",
        "clicks_gsc","impressions","ctr","position",
        "clicks_ads","cost","cpc","conversions",
        "expected_ctr","ctr_gap","organic_potential",
        "high_cpc_flag","reduce_bid_flag","priority"
    ]
    existing = [c for c in preferred if c in df.columns]
    df = df[existing + [c for c in df.columns if c not in existing]]

    return df
