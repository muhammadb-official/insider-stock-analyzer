import streamlit as st
import pandas as pd
import yfinance as yf

# -- MOCK INSIDER DATA (replace later with API) --
insider_trades = pd.DataFrame([
    {'ticker':'NVDA','buyer':'CEO Jensen Huang','position':'CEO','date':'2025-06-08','amount':8e6,'win_rate':0.93},
    {'ticker':'TSLA','buyer':'CEO Elon Musk','position':'CEO','date':'2025-06-08','amount':5e6,'win_rate':0.91},
])

# -- FINANCIAL FETCH & HALAL LOGIC --
def fetch_financials(tkr):
    stock = yf.Ticker(tkr)
    i = stock.info
    return {
        'PE': i.get('trailingPE'),
        'PEG': i.get('pegRatio'),
        'ROE': i.get('returnOnEquity')*100 if i.get('returnOnEquity') else None,
        'Quick': i.get('quickRatio'),
        'RevGrowth': i.get('revenueGrowth')*100 if i.get('revenueGrowth') else None,
        'Halal': True  # Basic placeholder
    }

def recommend(f):
    if not f['Halal']:
        return 'Exclude'
    if f['PE'] and f['PEG'] and f['ROE'] and f['Quick'] and f['PEG'] < 2 and f['ROE'] > 20 and f['Quick'] > 1:
        return 'Buy Now'
    if f['PEG'] and f['PEG'] > 2 or (f['Quick'] and f['Quick'] < 1):
        return 'Wait'
    return 'Hold'

# -- APP LAYOUT --
st.title("🚀 Insider Trade + Halal Compliance Dashboard")
st.write("Automatically analyzes high-success insider buys (win rate ≥ 90%)")

df = insider_trades[insider_trades['win_rate'] >= 0.90].copy()
results = []

for _, r in df.iterrows():
    fin = fetch_financials(r['ticker'])
    rec = recommend(fin)
    entry = {**r.to_dict(), **fin, 'Recommendation': rec}
    results.append(entry)

res_df = pd.DataFrame(results)
filters = st.sidebar

if filters.checkbox("Halal only", value=True):
    res_df = res_df[res_df['Halal']==True]

st.dataframe(res_df)

st.write("✅ Strong buys:")
st.write(res_df[res_df['Recommendation']=='Buy Now'])
