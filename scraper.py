import csv
from datetime import datetime
import random
import time

# Placeholder scraper to simulate real results
def fetch_trades():
    print("🔍 Simulating trade scraping...")
    time.sleep(2)

    fake_data = [
        {
            "ticker": "MSFT",
            "buyer": "Satya Nadella",
            "position": "CEO",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 3000000,
            "source": "Insider",
            "PE": 38.91,
            "PEG": "None",
            "ROE": 33.61,
            "Quick": 1.244,
            "RevGrowth": 13.3,
            "Halal": True,
        },
        {
            "ticker": "AAPL",
            "buyer": "Tim Cook",
            "position": "CEO",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": random.randint(500000, 2000000),
            "source": "Insider",
            "PE": 28.5,
            "PEG": 1.2,
            "ROE": 29.0,
            "Quick": 1.12,
            "RevGrowth": 9.4,
            "Halal": True,
        },
    ]
    return fake_data

def save_to_csv(data, filename="scraped_trades.csv"):
    print(f"📦 Saving {len(data)} trades to {filename}...")
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("✅ Data saved successfully.")

if __name__ == "__main__":
    print("🚀 Starting scraper.py...")
    trades = fetch_trades()
    save_to_csv(trades)
    print("🏁 Scraper finished.")
