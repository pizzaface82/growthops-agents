import streamlit as st
from src.digest import run_digest

st.set_page_config(page_title="GrowthOps Digest", layout="centered")
st.title("Performance Overview")

if st.button("Run Digest Now"):
    res = run_digest()
    st.subheader("GA4")
    st.json(res["ga4"])
    st.subheader("Shopify")
    st.json(res["shopify"])
    st.subheader("Summary")
    st.write(res["summary"])
    st.success("Posted to Slack (if webhook configured).")
