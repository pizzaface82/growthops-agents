import streamlit as st
import pandas as pd
from src.digest import run_digest

st.set_page_config(page_title="GrowthOps Digest v2", page_icon="📈", layout="wide")
st.title("📈 GrowthOps Digest — Comparative View")

res = run_digest()
today, yday, deltas = res["today"], res["yesterday"], res["deltas"]

# KPI row
c1,c2,c3,c4 = st.columns(4)
c1.metric("Revenue", f"${today['revenue']:,}", f"{deltas['revenue_pct']:.2f}%", help=f"Yesterday: ${yday['revenue']:,}")
c2.metric("Purchases", f"{today['purchases']}", f"{deltas['purchases_pct']:.2f}%", help=f"Yesterday: {yday['purchases']}")
c3.metric("Users", f"{today['users']}", f"{deltas['users_pct']:.2f}%", help=f"Yesterday: {yday['users']}")
c4.metric("Sessions", f"{today['sessions']}", f"{deltas['sessions_pct']:.2f}%", help=f"Yesterday: {yday['sessions']}")

st.divider()

# Channel breakdown
st.subheader("Channel Breakdown")
st.bar_chart(res["channels"].set_index("channel")[["revenue","sessions"]])
st.dataframe(res["channels"].assign(conversion_rate = res["channels"]["revenue"]/res["channels"]["sessions"]).style.format({"conversion_rate":"{:.2%}","revenue":"${:,.0f}"}))

# Top products by channel
st.subheader("Top Converting Products by Channel")
st.dataframe(res["products"].style.format({"revenue":"${:,.0f}","cvr":"{:.1%}"}))

st.subheader("AI Summary")
st.markdown(res["summary"])
