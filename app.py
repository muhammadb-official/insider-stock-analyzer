import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import smtplib
from email.message import EmailMessage
import os

# Load Zoya API key from GitHub secrets
ZOYA_API_KEY = os.getenv("ZOYA_API_KEY")

# Mock insider trades for now
insider_trades = pd.DataFrame([
    {'ticker':'NVDA','buyer':'CEO Jensen Huang','position':'CEO','date':'2025-06-08','amount':8e6,'win_rate':0.93},
    {'ticker':'TSLA','buyer':'CEO Elon Musk','position':'CEO','date':'2025-06-08','amount':5e6,'win_rate':0.91},
])

def check_halal(ticker):
    try:
        headers = {"x-api-key": ZOYA_API_KEY}
        response = requests.get(f"https://api.zoya.finance/v1/screening/ticker/{ticker}", headers=headers)
        data = response.json()
        return data.get("isHalal", False)
    except:
        return False

def fetch_financials(tkr):
    stock = yf.Ticker(tkr)
    i = stock.info
    return {
        'PE': i.get('trailingPE'),
        'PEG': i.get('pegRatio'),
        'ROE': i.get('returnOnEquity')*100 if i.get('returnOnEquity') else None,
        'Quick': i.get('quickRatio'),
        'RevGrowth': i.get('revenueGrowth')*100 if i.get('revenueGrowth') else None,
    }

def recommend(f):
    try:
        if f['PE'] and f['PEG'] and f['ROE'] and f['Quick']:
            if f['PEG'] < 2 and f['ROE'] > 20 and f['Quick'] > 1:
                return 'Buy Now'
            elif f['PEG'] > 2 or f['Quick'] < 1:
                return 'Wait'
        return 'Hold'
    except:
        return 'Hold'

