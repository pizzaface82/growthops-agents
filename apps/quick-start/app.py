import streamlit as st
import pandas as pd
import requests

st.title("GrowthOps Quick-Start 🚀")
st.write("If you can see this, your environment is working!")

df = pd.DataFrame({
    "Phase": ["Setup", "Coding", "GitHub"],
    "Status": ["✅", "🧠", "🌍"]
})
st.dataframe(df)

