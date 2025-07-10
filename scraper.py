print("=== STARTING SCRAPER ===")

# ... your existing code ...

print("=== SCRAPER COMPLETE ===")
raise Exception("Debug test error to verify logs")

import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape_openinsider():
    print("Starting OpenInsider scrape...", flush=True)
    url = "https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdly=60&tdly=0&xp=1&vl=&vh=&t=&tc=1&ty=1&sortcol=0&maxresults=1000"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", class_="tinytable")
        rows = table.find_all("tr")[1:]

        data = []
        for row in rows:
            cols = [td.text.strip() for td in row.find_all("td")]
            if cols:
                data.append(cols)
        
        df = pd.DataFrame(data)
        print(f"✅ Scraped {len(df)} rows from OpenInsider.", flush=True)
        return df
    except Exception as e:
        print("❌ Failed to scrape OpenInsider:", e, flush=True)
        return pd.DataFrame()

def main():
    df = scrape_openinsider()

    if not df.empty:
        df.to_csv("scraped_trades.csv", index=False)
        print("✅ Saved scraped_trades.csv", flush=True)
    else:
        print("⚠️ No data scraped. CSV not updated.", flush=True)

if __name__ == "__main__":
    main()
print("=== STARTING SCRAPER ===")

# ... your existing code ...

print("=== SCRAPER COMPLETE ===")
