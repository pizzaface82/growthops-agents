import os
import pandas as pd
import streamlit as st

from apps.keyword_intel_agent.src.loaders import load_gsc_csv, load_ads_csv
from apps.keyword_intel_agent.src.metrics import add_kw_norm_cols, compute_overlap_segments, roi_signals
from apps.keyword_intel_agent.src.joiner import tidy_columns_for_display
from apps.keyword_intel_agent.src.ai import fallback_rules

# ---------- Page + state ----------
st.set_page_config(page_title="SEO ↔ SEM Keyword Intelligence", page_icon="🔎", layout="wide")
if "fuzzy" not in st.session_state: st.session_state.fuzzy = False
if "threshold" not in st.session_state: st.session_state.threshold = 90
if "api_mode" not in st.session_state: st.session_state.api_mode = False
if "use_samples" not in st.session_state: st.session_state.use_samples = True

# ---------- Helpers ----------
def read_samples():
    base = os.path.dirname(os.path.dirname(__file__))  # ui/ -> keyword_intel_agent/
    data_dir = os.path.join(base, "data")
    return (
        load_gsc_csv(os.path.join(data_dir, "sample_gsc.csv")),
        load_ads_csv(os.path.join(data_dir, "sample_ads.csv")),
    )

def resolve_inputs(gf, af, use_samples: bool):
    if use_samples or (gf is None and af is None):
        return read_samples()
    if gf is None or af is None:
        st.warning("Upload **both** GSC and Ads CSVs, or toggle **Use sample data**.")
        st.stop()
    return load_gsc_csv(gf), load_ads_csv(af)

def df_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def kpis(overlap, organic_only, paid_only):
    c1, c2, c3 = st.columns(3)
    c1.metric("Overlap (kw)", len(overlap))
    c2.metric("Organic-only (gaps)", len(organic_only))
    c3.metric("Paid-only (review)", len(paid_only))

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Inputs")
    st.session_state.use_samples = st.toggle("Use sample data", value=st.session_state.use_samples)
    gsc_file = st.file_uploader("GSC CSV (page, query, clicks, impressions, ctr, position)", type=["csv"])
    ads_file = st.file_uploader("Ads CSV (campaign, adgroup, keyword, clicks, cost, cpc, conversions)", type=["csv"])

    st.divider()
    st.header("Matching")
    st.session_state.fuzzy = st.checkbox("Enable fuzzy matching", value=st.session_state.fuzzy)
    st.session_state.threshold = st.slider("Fuzzy threshold", 70, 100, st.session_state.threshold, 1)

    st.divider()
    st.header("API mode (placeholder)")
    st.session_state.api_mode = st.checkbox("Use API mode (GA4/Ads connectors)", value=st.session_state.api_mode,
                                            help="Not wired yet — placeholder for future ingestion.")

    run = st.button("Run analysis", type="primary", use_container_width=True)

# ---------- Title ----------
st.title("🔎 SEO ↔ SEM Keyword Intelligence Agent")
st.caption("Compare GSC and Google Ads to find overlap, gaps, and wasted spend. Export weekly recommendations.")

# ---------- Pipeline ----------
if run:
    # Load
    gsc_df, ads_df = resolve_inputs(gsc_file, ads_file, st.session_state.use_samples)

    # Soft schema checks
    gsc_must = {"page","query","clicks","impressions","ctr","position"}
    ads_must = {"campaign","adgroup","keyword","clicks","cost","cpc","conversions"}
    miss_gsc = sorted(list(gsc_must - set(gsc_df.columns)))
    miss_ads = sorted(list(ads_must - set(ads_df.columns)))
    if miss_gsc: st.warning(f"GSC CSV missing: {', '.join(miss_gsc)}")
    if miss_ads: st.warning(f"Ads CSV missing: {', '.join(miss_ads)}")

    # Normalize + join
    gsc_df, ads_df = add_kw_norm_cols(gsc_df, ads_df)
    seg = compute_overlap_segments(gsc_df, ads_df, fuzzy=st.session_state.fuzzy, threshold=st.session_state.threshold)
    overlap = seg["overlap"]
    organic_only = seg["organic_only"]
    paid_only = seg["paid_only"]
    if not overlap.empty:
        overlap = roi_signals(overlap)

    st.success("Done!")
    kpis(overlap, organic_only, paid_only)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overlap", "Organic-Only", "Paid-Only", "Recommendations"])

    with tab1:
        st.subheader("Overlap (organic + paid)")
        if overlap.empty:
            st.info("No overlap found. Try fuzzy matching or adjust threshold.")
        else:
            tidy = tidy_columns_for_display(overlap)
            st.dataframe(tidy, use_container_width=True, height=420)
            st.download_button("Download Overlap CSV", df_bytes(tidy), "overlap.csv", "text/csv", use_container_width=True)

    with tab2:
        st.subheader("Organic-Only (opportunities to test in Ads)")
        tidy = tidy_columns_for_display(organic_only)
        st.dataframe(tidy, use_container_width=True, height=420)
        st.download_button("Download Organic-Only CSV", df_bytes(tidy), "organic_only.csv", "text/csv", use_container_width=True)

    with tab3:
        st.subheader("Paid-Only (ads without organic presence)")
        tidy = tidy_columns_for_display(paid_only)
        st.dataframe(tidy, use_container_width=True, height=420)
        st.download_button("Download Paid-Only CSV", df_bytes(tidy), "paid_only.csv", "text/csv", use_container_width=True)

    with tab4:
        st.subheader("Recommendations")
        md = fallback_rules(overlap, organic_only, paid_only)
        st.markdown(md)
        st.download_button("Download recommendations.md", md.encode("utf-8"), "recommendations.md", "text/markdown", use_container_width=True)

# Help expander
with st.expander("What’s happening under the hood"):
    st.markdown("""
- **pandas** loads CSVs, normalizes keywords → `kw_norm`
- **Join** on `kw_norm` (exact) or via **RapidFuzz** mapping (fuzzy)
- **Signals** on Overlap: expected CTR → CTR gap → `organic_potential`; flags for CPC/rank
- **Output**: 3 tables + actionable Markdown summary
""")
