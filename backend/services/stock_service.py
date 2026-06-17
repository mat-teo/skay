# backend/services/stock_service.py
import os
import json
import urllib.request
from typing import List, Dict, Any, Optional
from models import UserStock
import time

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")

# Internal cache to avoid excessive API calls (5 minutes timeout)
_price_cache = {}
_cache_timeout = 300 

def get_stock_price_sync(ticker: str) -> Optional[float]:
    """
    Fetch the current price for a stock ticker.
    1. Check the in-memory cache.
    2. Query the Yahoo Finance Chart API directly (Docker-safe for EU and US).
    3. Fallback to Alpha Vantage if Yahoo Finance fails.
    """
    ticker = ticker.upper()
    
    # Check cache first
    if ticker in _price_cache:
        price_data = _price_cache[ticker]
        if time.time() - price_data['timestamp'] < _cache_timeout:
            return price_data['price']
    
    # STRATEGY 1: Direct Yahoo Finance API request (Bypasses yfinance library rate limits)
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=7) as response:
            data = json.loads(response.read().decode())
            result = data.get('chart', {}).get('result', [])
            if result and len(result) > 0:
                meta = result[0].get('meta', {})
                price = meta.get('regularMarketPrice') or meta.get('chartPreviousClose')
                if price:
                    print(f"Yahoo Direct API: {ticker} = {price}")
                    return _cache_price(ticker, float(price))
    except Exception as e:
        print(f"Yahoo Direct API failed for {ticker}: {e}")
    
    # STRATEGY 2: Fallback to Alpha Vantage API (Best for US tickers)
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=7) as response:
            data = json.loads(response.read().decode())
            quote = data.get('Global Quote', {})
            price_str = quote.get('05. price')
            if price_str:
                price = float(price_str)
                print(f"Alpha Vantage Fallback: {ticker} = {price}")
                return _cache_price(ticker, price)
    except Exception as e:
            print(f"Alpha Vantage error for {ticker}: {e}")
    except Exception as e:
        print(f"Alpha Vantage connection error for {ticker}: {e}")
    
    return None

def _cache_price(ticker: str, price: float) -> float:
    """Store the fetched price in the local memory cache."""
    _price_cache[ticker] = {
        'price': price,
        'timestamp': time.time()
    }
    return price

def clear_price_cache():
    """Clear the entire in-memory price cache."""
    global _price_cache
    _price_cache = {}

def calculate_portfolio_value(stocks: List[UserStock], prices: Dict[str, float]) -> Dict[str, Any]:
    """Calculate total portfolio metrics based on current cached prices."""
    total_value = 0
    total_cost = 0
    
    for stock in stocks:
        current_price = prices.get(stock.ticker, 0)
        total_value += current_price * stock.quantity
        total_cost += stock.average_buy_price * stock.quantity
    
    total_gain = total_value - total_cost
    total_gain_percent = (total_gain / total_cost * 100) if total_cost > 0 else 0
    
    return {
        "total_value": total_value,
        "total_cost": total_cost,
        "total_gain": total_gain,
        "total_gain_percent": total_gain_percent
    }