import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

# List of free proxies (update weekly!)
proxies = [
    "http://198.59.191.234:8080",
    "http://103.160.201.76:10000",
    "http://64.225.8.82:9981",
    "http://159.203.61.169:3128",
    "http://194.233.78.113:3128"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

def fetch_with_proxy(url, max_retries=5):
    for attempt in range(max_retries):
        proxy = {"http": random.choice(proxies), "https": random.choice(proxies)}
        try:
            print(f"Attempt {attempt+1} using proxy: {proxy['http']}")
            response = requests.get(url, headers=headers, proxies=proxy, timeout=15)
            if response.status_code == 200:
                return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            time.sleep(2)  # short pause before retry
    raise Exception("All proxy attempts failed.")

def scrape_openinsider():
    url = "https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdly=60&tdly=0&xp=1&vl=&vh=&t=&tc=1&ty=1&sortcol=0&maxresults=1000"
    r = fetch_with_proxy(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", class_="tinytable")
    if not table:
        raise Exception("Data table not found on page.")

    rows = table.find_all("tr")[1:]
    data = []
    for row in rows:
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:
            data.append(cols)

    df = pd.DataFrame(data)
    return df

def scrape_congress():
    # Stub: Replace with real logic if needed
    return pd.DataFrame()

def scrape_sec():
    # Stub: Replace with real logic if needed
    return pd.DataFrame()

if __name__ == "__main__":
    try:
        df = pd.concat([scrape_openinsider(), scrape_congress(), scrape_sec()])
        df.to_csv("scraped_trades.csv", index=False)
        print("✅ Scrape successful. Data saved to scraped_trades.csv")
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        exit(1)
