import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os

# -----------------------------
# Load Data
# -----------------------------
if os.path.exists("scraped_trades.csv"):
    df = pd.read_csv("scraped_trades.csv")
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= datetime.now() - pd.Timedelta(days=60)]
else:
    df = pd.DataFrame(columns=["ticker", "buyer", "position", "date", "amount", "source"])

# -----------------------------
# Halal Check
# -----------------------------
def check_halal_manual(ticker):
    try:
        info = yf.Ticker(ticker).info
        market_cap = info.get('marketCap', 1)
        debt = info.get('totalDebt', 0)
        cash = info.get('totalCash', 0)
        receivables = info.get('totalReceivables', 0)
        return (debt / market_cap < 0.33 and cash / market_cap < 0.33 and receivables / market_cap < 0.49)
    except:
        return False

# -----------------------------
# Financial Metrics + Logic
# -----------------------------
def fetch_financials(tkr):
    try:
        info = yf.Ticker(tkr).info
        return {
            'PE': info.get('trailingPE'),
            'PEG': info.get('pegRatio'),
            'ROE': (info.get('returnOnEquity') or 0) * 100,
            'Quick': info.get('quickRatio'),
            'RevGrowth': (info.get('revenueGrowth') or 0) * 100,
        }
    except:
        return {}

def recommend(f):
    try:
        if f['PEG'] and f['PEG'] < 2 and f['ROE'] > 20 and f['Quick'] > 1:
            return 'Buy Now'
        elif f['PEG'] and (f['PEG'] > 2 or f['Quick'] < 1):
            return 'Wait'
        else:
            return 'Hold'
    except:
        return 'Hold'

# -----------------------------
# Analyze Each Row
# -----------------------------
results = []
for _, r in df.iterrows():
    fin = fetch_financials(r['ticker'])
    halal = check_halal_manual(r['ticker'])
    rec = recommend(fin) if halal else "Not Halal"
    results.append({**r, **fin, 'Halal': halal, 'Recommendation': rec})

res_df = pd.DataFrame(results)

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(layout="wide")
st.title("📈 Halal Trade Analyzer (Insider, Congress, Institutional)")

st.sidebar.header("🔍 Filters")
if 'Halal' in res_df.columns and st.sidebar.checkbox("✅ Halal Only", value=True):
    res_df = res_df[res_df['Halal'] == True]
if 'Recommendation' in res_df.columns and st.sidebar.checkbox("⭐ Buy Now Only"):
    res_df = res_df[res_df['Recommendation'] == 'Buy Now']
ticker_filter = st.sidebar.text_input("🔎 Ticker")
if ticker_filter:
    res_df = res_df[res_df['ticker'].str.contains(ticker_filter.upper(), na=False)]

st.subheader("📋 Final Trade Picks (Last 60 Days)")
st.dataframe(res_df, use_container_width=True)

# -----------------------------
# Email Summary (Optional)
# -----------------------------
def send_email(df):
    EMAIL_ADDRESS = "your_email@gmail.com"
    EMAIL_PASSWORD = "your_app_password"
    msg = EmailMessage()
    msg['Subject'] = 'Halal Trade Summary'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = "muhammad_bangi@hotmail.com"
    msg.set_content("Daily halal insider trade picks.")
    msg.add_alternative(df.to_html(index=False), subtype='html')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

if not res_df.empty and st.button("📧 Send Email Summary"):
    send_email(res_df)
    st.success("✅ Email sent")
