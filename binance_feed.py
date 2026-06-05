import requests
import streamlit as st

BASE_URL = "https://api.binance.com/api/v3"


# =========================
# COINS (200 list)
# =========================
import requests

BASE_URL = "https://api.binance.com/api/v3"

def get_top_coins(limit=200):

    try:
        r = requests.get(f"{BASE_URL}/exchangeInfo", timeout=10)
        data = r.json()

        # 🧠 SAFETY CHECK (IMPORTANT)
        if not isinstance(data, dict):
            return []

        if "symbols" not in data:
            return []

        coins = []

        for s in data["symbols"]:
            if (
                isinstance(s, dict)
                and s.get("status") == "TRADING"
                and s.get("symbol", "").endswith("USDT")
            ):
                coins.append(s["symbol"])

        return coins[:limit]

    except Exception as e:
        return []


# =========================
# PRICE
# =========================
@st.cache_data(ttl=10)
def get_price(symbol):

    try:
        r = requests.get(
            f"{BASE_URL}/ticker/price",
            params={"symbol": symbol},
            timeout=10
        )
        return float(r.json()["price"])

    except:
        return None


# =========================
# CANDLES
# =========================
@st.cache_data(ttl=10)
def get_candles(symbol, limit=50):

    try:
        r = requests.get(
            f"{BASE_URL}/klines",
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
