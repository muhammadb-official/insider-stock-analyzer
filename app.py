import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage

# -----------------------------
# STEP 1: Live Insider Scraper
# -----------------------------
def scrape_openinsider(days=60):
    url = "https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdly=60&tdly=0&xp=1&vl=&vh=&t=&tc=1&ty=1&sortcol=0&maxresults=1000"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("table", {"class": "tinytable"})
    rows = table.find_all("tr")[1:] if table else []
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 11: continue
        try:
            date = datetime.strptime(cols[2].text.strip(), '%Y-%m-%d')
            if date < datetime.now() - timedelta(days=days): continue
            ticker = cols[1].text.strip()
            name = cols[0].text.strip()
            title = cols[3].text.strip()
            trade_type = cols[6].text.strip()
            amount = int(cols[10].text.replace(',', '').replace('$', '').strip() or 0)
            if 'P' in trade_type:
                data.append({
                    'ticker': ticker, 'buyer': name, 'position': title,
                    'date': date, 'amount': amount, 'win_rate': None, 'source': 'Insider'
                })
        except: continue
    return pd.DataFrame(data)

# -----------------------------
# STEP 2: Congress Trade Scraper
# -----------------------------
def scrape_congress_trades(days=60):
    url = "https://housestockwatcher.com/api/transactions"
    response = requests.get(url)
    records = response.json()
    data = []
    for r in records:
        try:
            date = datetime.strptime(r['transaction_date'], '%Y-%m-%d')
            if date < datetime.now() - timedelta(days=days): continue
            if r['type'].lower() == 'purchase':
                data.append({
                    'ticker': r['ticker'], 'buyer': r['representative'],
                    'position': 'Congress', 'date': date,
                    'amount': 0, 'win_rate': None, 'source': 'Congress'
                })
        except: continue
    return pd.DataFrame(data)

# -----------------------------
# STEP 3: SEC Institutional Scraper (13D/13G)
# -----------------------------
def scrape_sec_13dg(days=60):
    # S&P 500 companies (partial for demo)
    sp500_companies = ['Apple Inc.', 'Microsoft Corporation', 'NVIDIA Corporation', 'Alphabet Inc.', 'Meta Platforms, Inc.']
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=SC%2013&count=100"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')[1:]
    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 4: continue
        try:
            date_str = cols[3].text.strip()
            date = datetime.strptime(date_str, '%Y-%m-%d')
            if date < datetime.now() - timedelta(days=days): continue
            filer = cols[0].text.strip()
            if any(name.lower() in filer.lower() for name in sp500_companies):
                link = "https://www.sec.gov" + cols[1].find('a')['href']
                target = cols[2].text.strip()
                data.append({
                    'ticker': target, 'buyer': filer,
                    'position': 'Institutional', 'date': date,
                    'amount': 0, 'win_rate': None, 'source': 'Institutional'
                })
        except: continue
    return pd.DataFrame(data)

# -----------------------------
# STEP 4: Halal Filter
# -----------------------------
def check_halal_manual(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        market_cap = info.get('marketCap', 1)
        debt = info.get('totalDebt', 0)
        cash = info.get('totalCash', 0)
        receivables = info.get('totalReceivables', 0)
        if not market_cap or market_cap == 0:
            return False
        return (debt / market_cap < 0.33 and cash / market_cap < 0.33 and receivables / market_cap < 0.49)
    except:
        return False

# -----------------------------
# STEP 5: Financial Analysis
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
# STEP 6: Streamlit UI
# -----------------------------
st.set_page_config(layout="wide")
st.title("📊 Halal Trade Watch – Insider | Congress | Institutional")

with st.spinner("🔄 Scraping data (OpenInsider, Congress, SEC)..."):
    insider_df = scrape_openinsider()
    congress_df = scrape_congress_trades()
    institutional_df = scrape_sec_13dg()
    combined = pd.concat([insider_df, congress_df, institutional_df])
    combined['date'] = pd.to_datetime(combined['date'])
    combined = combined[combined['date'] >= datetime.now() - timedelta(days=60)]

results = []
for _, r in combined.iterrows():
    fin = fetch_financials(r['ticker'])
    halal = check_halal_manual(r['ticker'])
    rec = recommend(fin) if halal else "Not Halal"
    results.append({**r, **fin, 'Halal': halal, 'Recommendation': rec})

df = pd.DataFrame(results)

st.sidebar.header("🔍 Filters")
if st.sidebar.checkbox("✅ Halal Only", value=True):
    df = df[df['Halal'] == True]
if st.sidebar.checkbox("⭐ Buy Now Only"):
    df = df[df['Recommendation'] == 'Buy Now']
ticker_filter = st.sidebar.text_input("🔎 Search by Ticker")
if ticker_filter:
    df = df[df['ticker'].str.contains(ticker_filter.upper(), na=False)]

st.subheader("📋 Final Trade Picks (Last 60 Days)")
st.dataframe(df, use_container_width=True)

# -----------------------------
# STEP 7: Email Summary
# -----------------------------
def send_email(df):
    EMAIL_ADDRESS = "your_email@gmail.com"
    EMAIL_PASSWORD = "your_app_password"
    msg = EmailMessage()
    msg['Subject'] = 'Halal Trade Picks'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = "muhammad_bangi@hotmail.com"
    msg.set_content("Your daily halal stock trade alerts.")
    msg.add_alternative(df.to_html(index=False), subtype='html')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

if st.button("📧 Send Email Summary"):
    send_email(df)
    st.success("✅ Email sent to muhammad_bangi@hotmail.com")
