import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def scrape_openinsider():
    try:
        print("Scraping OpenInsider...")
        url = "https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdly=60&tdly=0&xp=1&vl=&vh=&t=&tc=1&ty=1&sortcol=0&maxresults=1000"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", class_="tinytable")
        df = pd.read_html(str(table))[0]
        df = df.rename(columns={"Ticker": "ticker", "Filer Name": "buyer", "Title": "position", "Trade Date": "date", "Qty": "amount"})
        df = df[["ticker", "buyer", "position", "date", "amount"]]
        df["source"] = "Insider"
        print(f"✅ OpenInsider rows: {len(df)}")
        return df
    except Exception as e:
        print(f"❌ Error scraping OpenInsider: {e}")
        return pd.DataFrame()

def scrape_congress():
    try:
        print("Scraping Congress trades...")
        url = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
        r = requests.get(url, timeout=30)
        data = r.json()
        df = pd.DataFrame(data)
        df = df[df["transaction_date"] >= (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")]
        df = df.rename(columns={"ticker": "ticker", "representative": "buyer", "type": "position", "transaction_date": "date", "amount": "amount"})
        df = df[["ticker", "buyer", "position", "date", "amount"]]
        df["source"] = "Congress"
        print(f"✅ Congress rows: {len(df)}")
        return df
    except Exception as e:
        print(f"❌ Error scraping Congress: {e}")
        return pd.DataFrame()

def scrape_sec():
    try:
        print("Scraping SEC Institutional filings (placeholder)...")
        url = "https://www.sec.gov/files/company_tickers_exchange.json"
        r = requests.get(url, timeout=30)
        data = r.json()
        rows = []
        for company in data[:3]:  # limit for demo
            rows.append({
                "ticker": company.get("ticker", ""),
                "buyer": company.get("title", ""),
                "position": "Institution",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "amount": 0,
                "source": "Institution"
            })
        df = pd.DataFrame(rows)
        print(f"✅ SEC filings rows: {len(df)}")
        return df
    except Exception as e:
        print(f"❌ Error scraping SEC: {e}")
        return pd.DataFrame()

# Run all scrapers
df_open = scrape_openinsider()
df_congress = scrape_congress()
df_sec = scrape_sec()

# Combine and save
df = pd.concat([df_open, df_congress, df_sec], ignore_index=True)
print(f"📦 Total combined rows: {len(df)}")
df.to_csv("scraped_trades.csv", index=False)
