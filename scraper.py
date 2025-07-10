import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import re
import traceback

# Optional: use a free proxy (can be rotated or upgraded later)
proxies = {
    "http": "http://159.203.61.169:3128",
    "https": "http://159.203.61.169:3128"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_openinsider():
    try:
        url = "https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdly=60&tdly=0&xp=1&vl=&vh=&t=&tc=1&ty=1&sortcol=0&maxresults=1000"
        r = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("table.tinytable tr")[1:]
        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 9:
                data.append({
                    "ticker": cols[1].text.strip(),
                    "buyer": cols[3].text.strip(),
                    "position": cols[4].text.strip(),
                    "date": cols[5].text.strip(),
                    "amount": cols[8].text.strip().replace(",", ""),
                    "source": "Insider"
                })
        return pd.DataFrame(data)
    except Exception as e:
        print("Error scraping OpenInsider:", e)
        traceback.print_exc()
        return pd.DataFrame()

def scrape_congress():
    try:
        url = "https://housestockwatcher.com/trades"
        r = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        df_list = pd.read_html(r.text)
        df = df_list[0]
        df["source"] = "Congress"
        df.rename(columns={
            "Ticker": "ticker",
            "Transaction Date": "date",
            "Representative": "buyer",
            "Amount": "amount"
        }, inplace=True)
        df["position"] = ""
        return df[["ticker", "buyer", "position", "date", "amount", "source"]]
    except Exception as e:
        print("Error scraping Congress:", e)
        traceback.print_exc()
        return pd.DataFrame()

def scrape_sec():
    try:
        url = "https://whalewisdom.com/filer/13d-filings"
        r = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("table.table tr")[1:]
        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 4:
                data.append({
                    "ticker": cols[1].text.strip(),
                    "buyer": cols[2].text.strip(),
                    "position": "Institution",
                    "date": cols[4].text.strip(),
                    "amount": "",
                    "source": "Institutional"
                })
        return pd.DataFrame(data)
    except Exception as e:
        print("Error scraping SEC 13D:", e)
        traceback.print_exc()
        return pd.DataFrame()

# MAIN EXECUTION

df = pd.concat([
    scrape_openinsider(),
    scrape_congress(),
    scrape_sec()
], ignore_index=True)

# Save results
df.to_csv("scraped_trades.csv", index=False)
print("Scraping complete. Total records:", len(df))
