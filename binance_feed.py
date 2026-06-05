import requests
import streamlit as st

BASE = "https://api.binance.com/api/v3"

# =========================
# COINS
# =========================
@st.cache_data(ttl=3600)
def get_top_coins(limit=100):
    try:
        r = requests.get(f"{BASE}/ticker/24hr", timeout=10)
        data = r.json()

        if not isinstance(data, list):
            return []

        coins = [
            x["symbol"]
            for x in data
            if isinstance(x, dict)
            and x.get("symbol", "").endswith("USDT")
        ]

        return coins[:limit]

    except:
        return ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]


# =========================
# PRICE (FIXED)
# =========================
@st.cache_data(ttl=10)
def get_price(symbol):
    try:
        r = requests.get(f"{BASE}/ticker/price", params={"symbol": symbol}, timeout=10)
        data = r.json()
        return float(data["price"])
    except:
        return None


# =========================
# CANDLES (FIXED)
# =========================
@st.cache_data(ttl=10)
def get_candles(symbol, limit=50):
    try:
        r = requests.get(
            f"{BASE}/klines",
            params={"symbol": symbol, "interval": "1m", "limit": limit},
            timeout=10
        )
        data = r.json()

        candles = []
        for c in data:
            candles.append({
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4])
            })

        return candles

    except:
        return []
