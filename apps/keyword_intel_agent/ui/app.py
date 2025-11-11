import os
import pandas as pd
import streamlit as st

from apps.keyword_intel_agent.src.loaders import load_gsc_csv, load_ads_csv
from apps.keyword_intel_agent.src.metrics import add_kw_norm_cols, compute_overlap_segments, roi_signals
from apps.keyword_intel_agent.src.joiner import tidy_columns_for_display
from apps.keyword_intel_agent.src.ai import fallback_rules

st.set_page_config(page_title="SEO ↔ SEM Keyword Intelligence", layout="wide")
st.title("🔎 SEO ↔ SEM Keyword Intelligence Agent")

with st.sidebar:
    st.header("Inputs")
    fuzzy = st.checkbox("Enable fuzzy matching", value=False)
    threshold = st.slider("Fuzzy threshold", min_value=70, max_value=100, value=90, step=1)
    st.caption("Tip: Start exact, then try fuzzy ~90 for variant mapping.")

col1, col2 = st.columns(2)
with col1:
    gsc_file = st.file_uploader(
        "GSC CSV (page, query, clicks, impressions, ctr, position)",
        type=["csv"], key="gsc"
    )
with col2:
    ads_file = st.file_uploader(
        "Ads CSV (campaign, adgroup, keyword, clicks, cost, cpc, conversions)",
        type=["csv"], key="ads"
    )

def load_samples_if_needed(gf, af):
    base = os.path.dirname(os.path.dirname(__file__))  # ui/ -> keyword_intel_agent/
    data_dir = os.path.join(base, "data")
    gsc_path = os.path.join(data_dir, "sample_gsc.csv")
    ads_path = os.path.join(data_dir, "sample_ads.csv")
    gsc = load_gsc_csv(gf if gf else gsc_path)
    ads = load_ads_csv(af if af else ads_path)
    return gsc, ads

if st.button("Run analysis", type="primary"):
    with st.spinner("Loading & joining…"):
        gsc_df, ads_df = load_samples_if_needed(gsc_file, ads_file)
        gsc_df, ads_df = add_kw_norm_cols(gsc_df, ads_df)
        seg = compute_overlap_segments(gsc_df, ads_df, fuzzy=fuzzy, threshold=threshold)
        overlap = seg["overlap"]
        organic_only = seg["organic_only"]
        paid_only = seg["paid_only"]
        if not overlap.empty:
            overlap = roi_signals(overlap)
    st.success("Done!")

    tab1, tab2, tab3, tab4 = st.tabs(["Overlap", "Organic-Only", "Paid-Only", "Recommendations"])

    with tab1:
        st.subheader("Overlap (organic + paid)")
        if overlap.empty:
            st.warning("No overlap found.")
        else:
            st.dataframe(tidy_columns_for_display(overlap).head(200), use_container_width=True)

    with tab2:
        st.subheader("Organic-Only (opportunities to test in Ads)")
        st.dataframe(tidy_columns_for_display(organic_only).head(200), use_container_width=True)

    with tab3:
        st.subheader("Paid-Only (ads without organic presence)")
        st.dataframe(tidy_columns_for_display(paid_only).head(200), use_container_width=True)

    with tab4:
        st.subheader("Recommendations")
        st.markdown(fallback_rules(overlap, organic_only, paid_only))
