import requests
import streamlit as st

# =========================
# API ENDPOINTS
# =========================
TOP_URL = "https://min-api.cryptocompare.com/data/top/mktcapfull"
PRICE_URL = "https://min-api.cryptocompare.com/data/price"


# =========================
# GET TOP COINS
# =========================
@st.cache_data(ttl=300)
def get_top_coins(limit=100):

    try:
        url = "https://min-api.cryptocompare.com/data/top/mktcapfull"

        params = {
            "tsym": "USD",
            "limit": 100
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        coins = []

        for item in data.get("Data", []):

            symbol = item.get("CoinInfo", {}).get("Name")

            if symbol:
                coins.append(symbol + "USDT")

        return coins[:limit]

    except Exception as e:
        st.error(f"API Error: {e}")
        return []


# =========================
# GET PRICE
# =========================
@st.cache_data(ttl=15)
def get_price(symbol):

    try:

        coin = symbol.replace("USDT", "")

        params = {
            "fsym": coin,
            "tsyms": "USD"
        }

        r = requests.get(
            PRICE_URL,
            params=params,
            timeout=10
        )

        data = r.json()

        return data.get("USD")

    except Exception as e:
        return None


# =========================
# GET CANDLES (IMPORTANT FIX)
# =========================
def get_candles(symbol, limit=50):

    try:

        coin = symbol.replace("USDT", "")

        url = "https://min-api.cryptocompare.com/data/v2/histominute"

        params = {
            "fsym": coin,
            "tsym": "USD",
            "limit": limit
        }

        r = requests.get(url, params=params, timeout=10)

        data = r.json().get("Data", {}).get("Data", [])

        candles = []

        for c in data:

            candles.append({
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"])
            })

        return candles

    except Exception as e:
        return []
