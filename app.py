import streamlit as st
import pandas as pd

st.set_page_config(page_title="Halal Trade Analyzer", layout="wide")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("scraped_trades.csv")
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filters")
halal_only = st.sidebar.checkbox("✅ Halal Only", value=True)
buy_now_only = st.sidebar.checkbox("⭐ Buy Now Only", value=False)
ticker_search = st.sidebar.text_input("🔎 Ticker")

# Apply filters
if halal_only:
    df = df[df["Halal"] == True]

if buy_now_only:
    df = df[
        (df["PEG"].astype(str) != "None") &
        (pd.to_numeric(df["PEG"], errors='coerce') <= 1.0) &
        (pd.to_numeric(df["PE"], errors='coerce') <= 20)
    ]

if ticker_search:
    df = df[df["ticker"].str.contains(ticker_search.upper(), na=False)]

# Display header
st.markdown("## 📊 Halal Trade Analyzer (Insider, Congress, Institutional)")
st.markdown("### 🗓️ Final Trade Picks (Last 60 Days)")
st.dataframe(df, use_container_width=True)

# Optional email button
st.button("📩 Send Email Summary (Coming Soon)")
