import streamlit as st
import pandas as pd
import yfinance as yf
import smtplib
from email.message import EmailMessage

# Mock insider trades
insider_trades = pd.DataFrame([
    {'ticker': 'NVDA', 'buyer': 'CEO Jensen Huang', 'position': 'CEO', 'date': '2025-06-08', 'amount': 8e6, 'win_rate': 0.93},
    {'ticker': 'TSLA', 'buyer': 'CEO Elon Musk', 'position': 'CEO', 'date': '2025-06-08', 'amount': 5e6, 'win_rate': 0.91},
])

# Manual Halal Screening (AAOIFI-compliant)
def check_halal_manual(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        market_cap = info.get('marketCap')
        total_debt = info.get('totalDebt', 0)
        cash = info.get('totalCash', 0)
        receivables = info.get('totalReceivables', 0)

        if not market_cap or market_cap == 0:
            return False

        debt_ratio = total_debt / market_cap
        cash_ratio = cash / market_cap
        receivables_ratio = receivables / market_cap

        return (debt_ratio < 0.33 and cash_ratio < 0.33 and receivables_ratio < 0.49)
    except Exception as e:
        st.error(f"Halal check failed for {ticker}: {e}")
        return False

# Pull financials
def fetch_financials(tkr):
    try:
        stock = yf.Ticker(tkr)
        i = stock.info
        return {
            'PE': i.get('trailingPE'),
            'PEG': i.get('pegRatio'),
            'ROE': i.get('returnOnEquity') * 100 if i.get('returnOnEquity') else None,
            'Quick': i.get('quickRatio'),
            'RevGrowth': i.get('revenueGrowth') * 100 if i.get('revenueGrowth') else None,
        }
    except Exception as e:
        st.error(f"Financial fetch failed for {tkr}: {e}")
        return {}

# Recommend action
def recommend(f):
    try:
        if f['PE'] and f['PEG'] and f['ROE'] and f['Quick']:
            if f['PEG'] < 2 and f['ROE'] > 20 and f['Quick'] > 1:
                return 'Buy Now'
            elif f['PEG'] > 2 or f['Quick'] < 1:
                return 'Wait'
        return 'Hold'
    except:
        return 'Hold'

# Email sending function
def send_email(df):
    EMAIL_ADDRESS = "your_email@gmail.com"
    EMAIL_PASSWORD = "your_app_password"
    msg = EmailMessage()
    msg['Subject'] = 'Daily Halal Stock Picks'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = "muhammad_bangi@hotmail.com"
    html = df.to_html(index=False)
    msg.set_content("Today's top stock picks.")
    msg.add_alternative(f"<h3>Buy Now + Halal Stocks</h3>{html}", subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# Streamlit UI
st.title("📈 Halal Insider Stock Analyzer")

df = insider_trades[insider_trades['win_rate'] >= 0.90].copy()
results = []

st.subheader("🧪 Debug: Processing Tickers")
for _, r in df.iterrows():
    st.write(f"🔍 Ticker: {r['ticker']}")
    fin = fetch_financials(r['ticker'])
    halal = check_halal_manual(r['ticker'])
    rec = recommend(fin) if halal else "Not Halal"
    entry = {**r.to_dict(), **fin, 'Halal': halal, 'Recommendation': rec}
    results.append(entry)

res_df = pd.DataFrame(results)

st.subheader("🧾 Raw Results (Before Filter)")
st.dataframe(res_df)

if st.sidebar.checkbox("✅ Show Only Halal", value=True):
    res_df = res_df[res_df['Halal'] == True]

st.subheader("📊 Final Filtered Results")
st.dataframe(res_df)

st.write("✅ **Buy Now + Halal Picks**")
buy_now_df = res_df[(res_df['Recommendation'] == 'Buy Now') & (res_df['Halal'] == True)]
st.write(buy_now_df)

if st.button("📤 Send Daily Email Now"):
    send_email(buy_now_df)
    st.success("✅ Email sent to muhammad_bangi@hotmail.com")
