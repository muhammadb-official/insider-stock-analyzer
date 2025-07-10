import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_openinsider():
    url = "http://openinsider.com/latest-cluster-buys"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="tinytable")

    trades = []
    if not table:
        print("No table found on page")
        return pd.DataFrame()

    rows = table.find_all("tr")[1:]  # skip header
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue

        try:
            ticker = cols[1].text.strip()
            buyer = cols[5].text.strip()
            position = cols[6].text.strip()
            date_str = cols[0].text.strip()
            date = datetime.strptime(date_str, "%Y-%m-%d")
            amount = int(cols[7].text.replace(",", "").replace("$", "").strip())
            source = "Insider"
        except Exception as e:
            continue

        trades.append({
            "ticker": ticker,
            "buyer": buyer,
            "position": position,
            "date": date,
            "amount": amount,
            "source": source
        })

    return pd.DataFrame(trades)

if __name__ == "__main__":
    df = scrape_openinsider()
    if not df.empty:
        df.to_csv("scraped_trades.csv", index=False)
        print(f"✅ Saved {len(df)} trades to scraped_trades.csv")
    else:
        print("⚠️ No trades found.")
