import requests
from requests_ip_rotator import ApiGateway
from bs4 import BeautifulSoup
import pandas as pd
import time

# === Set up AWS IP-rotator gateway for OpenInsider ===
gateway = ApiGateway("https://openinsider.com")
gateway.start()

# Mount adapter to route through API Gateway
session = requests.Session()
session.mount("https://openinsider.com", gateway)

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; HalalScraper/1.0; +https://yourdomain.com)"
}

def scrape_openinsider():
    url = "https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdly=60&tdly=0&xp=1&vl=&vh=&t=&tc=1&ty=1&sortcol=0&maxresults=1000"
    r = session.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", class_="tinytable")
    if not table:
        raise Exception("Could not find OpenInsider data table")
    rows = table.find_all("tr")[1:]
    data = [[td.text.strip() for td in row.find_all("td")] for row in rows]
    return pd.DataFrame(data)

def scrape_congress():
    # placeholder stub
    return pd.DataFrame()

def scrape_sec():
    # placeholder stub
    return pd.DataFrame()

if __name__ == "__main__":
    try:
        df = pd.concat([scrape_openinsider(), scrape_congress(), scrape_sec()], ignore_index=True)
        df.to_csv("scraped_trades.csv", index=False)
        print("✅ Scrape successful. Data saved.")
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        gateway.shutdown()
        exit(1)
    finally:
        gateway.shutdown()
