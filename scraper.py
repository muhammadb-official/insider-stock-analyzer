import requests
from bs4 import BeautifulSoup
import pandas as pd

# === Proxy Setup ===
proxies = {
    "http": "http://198.59.191.234:8080",    # You can swap this with a new one from sslproxies.org
    "https": "http://198.59.191.234:8080",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

def scrape_openinsider():
    url = "https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdly=60&tdly=0&xp=1&vl=&vh=&t=&tc=1&ty=1&sortcol=0&maxresults=1000"
    r = requests.get(url, headers=headers, proxies=proxies, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table", class_="tinytable")
    rows = table.find_all("tr")[1:]

    data = []
    for row in rows:
        cols = [td.text.strip() for td in row.find_all("td")]
        data.append(cols)

    df = pd.DataFrame(data)
    return df

def scrape_congress():
    # Dummy placeholder - add real logic if needed
    return pd.DataFrame()

def scrape_sec():
    # Dummy placeholder - add real logic if needed
    return pd.DataFrame()

if __name__ == "__main__":
    df = pd.concat([scrape_openinsider(), scrape_congress(), scrape_sec()])
    df.to_csv("scraped_trades.csv", index=False)
