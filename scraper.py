import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def scrape_openinsider():
    url = "https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdly=60&tdly=0&xp=1&vl=&vh=&t=&tc=1&ty=1&sortcol=0&maxresults=1000"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", class_="tinytable")
    df = pd.read_html(str(table))[0]
    df = df.rename(columns={"Ticker": "ticker", "Filer Name": "buyer", "Title": "position", "Trade Date": "date", "Qty": "amount"})
    df = df[["ticker", "buyer", "position", "date", "amount"]]
    df["source"] = "Insider"
    return df

def scrape_congress():
    url = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame(data)
    df = df[df["transaction_date"] >= (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")]
    df = df.rename(columns={"ticker": "ticker", "representative": "buyer", "type": "position", "transaction_date": "date", "amount": "amount"})
    df = df[["ticker", "buyer", "position", "date", "amount"]]
    df["source"] = "Congress"
    return df

def scrape_sec():
    url = "https://www.sec.gov/files/company_tickers_exchange.json"
    r = requests.get(url)
    data = r.json()
    rows = []
    for company in data:
        rows.append({
            "ticker": company.get("ticker", ""),
            "buyer": company.get("title", ""),
            "position": "Institution",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": 0,
            "source": "Institution"
        })
    return pd.DataFrame(rows)

# Skip all halal filtering logic
df = pd.concat([scrape_openinsider(), scrape_congress(), scrape_sec()], ignore_index=True)
df.to_csv("scraped_trades.csv", index=False)
