import streamlit as st
import pandas as pd
import yfinance as yf
import smtplib
from email.message import EmailMessage

# -----------------------------
# STEP 1: Simulated Insider Trade Feed (Replace w/API/scraping)
# -----------------------------
insider_trades = pd.DataFrame([
    {'ticker': 'MSFT', 'buyer': 'Satya Nadella', 'position': 'CEO', 'date': '2025-06-07', 'amount': 3000000, 'win_rate': 0.92},
    {'ticker': 'AAPL', 'buyer': 'Tim Cook', 'position': 'CEO', 'date': '2025-06-07', 'amount': 5000000, 'win_rate': 0.90},
    {'ticker': 'NVDA', 'buyer': 'Senator John Doe', 'position': 'Senator', 'date': '2025-06-07', 'amount': 200000, 'win_rate': 0.91},
    {'ticker': 'META', 'buyer': 'Rep. Jane Smith', 'position': 'House Rep', 'date': '2025-06-07', 'amount': 150000, 'win_rate': 0.93},
])

# Filter for insiders with high win rate
df = insider_trades[insider_trades['win_rate'] >= 0.90].copy()

# -----------------------------
# STEP 2: Manual Halal Screening
# -----------------------------
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

# -----------------------------
# STEP 3: Financial Metrics + Recommendation
# -----------------------------
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

# -----------------------------
# STEP 4: Email Output
# -----------------------------
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

# -----------------------------
# STEP 5: Main Streamlit App
# -----------------------------
st.title("📈 Halal Insider Trade Analyzer")

results = []
st.subheader("🧪 Processing Trades...")
for _, r in df.iterrows():
    st.write(f"🔍 Ticker: {r['ticker']}")
    fin = fetch_financials(r['ticker'])
    halal = check_halal_manual(r['ticker'])
    rec = recommend(fin) if halal else "Not Halal"
    entry = {**r.to_dict(), **fin, 'Halal': halal, 'Recommendation': rec}
    results.append(entry)

res_df = pd.DataFrame(results)

# Show full unfiltered table
st.subheader("🧾 Raw Results")
st.dataframe(res_df)

# Sidebar filter
if st.sidebar.checkbox("✅ Show Only Halal", value=True):
    res_df = res_df[res_df['Halal'] == True]

st.subheader("📊 Final Filtered Results")
st.dataframe(res_df)

st.write("✅ **Buy Now + Halal Picks**")
buy_now_df = res_df[(res_df['Recommendation'] == 'Buy Now') & (res_df['Halal'] == True)]
st.write(buy_now_df)

# Manual email trigger
if st.button("📤 Send Daily Email Now"):
    send_email(buy_now_df)
    st.success("✅ Email sent to muhammad_bangi@hotmail.com")
