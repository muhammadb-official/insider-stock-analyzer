import streamlit as st
import pandas as pd

st.set_page_config(page_title="Halal Trade Analyzer", layout="wide")
st.title("📈 Halal Trade Analyzer (Insider Only)")

try:
    df = pd.read_csv("scraped_trades.csv")
    st.dataframe(df)
except FileNotFoundError:
    st.warning("⚠️ scraped_trades.csv not found.")
