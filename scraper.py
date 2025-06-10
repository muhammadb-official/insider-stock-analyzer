# scraper.py
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

headers = {'User-Agent': 'Mozilla/5.0'}
days = 60
cutoff = datetime.now() - timedelta(days=days)

# Scrape OpenInsider
def scrape_openinsider():
    url = "https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdly=60&tdly=0&xp=1&vl=&vh=&t=&tc=1&ty=1&sortcol=0&maxresults=1000"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find_all("tr")[1:]
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 11: continue
        try:
            date = datetime.strptime(cols[2].text.strip(), '%Y-%m-%d')
            if date < cutoff: continue
            if 'P' not in cols[6].text.strip(): continue
            data.append({
                'ticker': cols[1].text.strip(),
                'buyer': cols[0].text.strip(),
                'position': cols[3].text.strip(),
                'date': date.strftime('%Y-%m-%d'),
                'amount': int(cols[10].text.replace('$','').replace(',','').strip() or 0),
                'source': 'Insider'
            })
        except: continue
    return pd.DataFrame(data)

# Scrape Congress
def scrape_congress():
    r = requests.get("https://housestockwatcher.com/api/transactions", headers=headers)
    recs = r.json()
    data = []
    for rec in recs:
        try:
            d = datetime.strptime(rec['transaction_date'], '%Y-%m-%d')
            if d < cutoff: continue
            if rec['type'].lower() != 'purchase': continue
            data.append({
                'ticker': rec['ticker'],
                'buyer': rec['representative'],
                'position': 'Congress',
                'date': d.strftime('%Y-%m-%d'),
                'amount': 0,
                'source': 'Congress'
            })
        except: continue
    return pd.DataFrame(data)

# Scrape SEC 13D/13G
def scrape_sec():
    sp500_companies = ['Apple Inc.', 'Microsoft Corporation', 'NVIDIA Corporation', 'Meta Platforms, Inc.', 'Alphabet Inc.']
    r = requests.get("https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=SC%2013&count=100", headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find_all('tr')[1:]
    data = []
    for row in rows:
        try:
            cols = row.find_all('td')
            d = datetime.strptime(cols[3].text.strip(), '%Y-%m-%d')
            if d < cutoff: continue
            filer = cols[0].text.strip()
            if any(c.lower() in filer.lower() for c in sp500_companies):
                data.append({
                    'ticker': cols[2].text.strip(),
                    'buyer': filer,
                    'position': 'Institutional',
                    'date': d.strftime('%Y-%m-%d'),
                    'amount': 0,
                    'source': 'Institutional'
                })
        except: continue
    return pd.DataFrame(data)

# Save final output
df = pd.concat([scrape_openinsider(), scrape_congress(), scrape_sec()])
df.to_csv("scraped_trades.csv", index=False)
print("✅ Scraped and saved to scraped_trades.csv")
