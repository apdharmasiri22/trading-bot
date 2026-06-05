import requests
import streamlit as st


TOP_URL = "https://api.binance.com/api/v3/exchangeInfo"


@st.cache_data(ttl=600)
def get_top_coins(limit=200):

    try:
        r = requests.get(TOP_URL, timeout=10)
        data = r.json()

        if "symbols" not in data:
            return []

        coins = []

        for symbol in data["symbols"]:

            if (
                isinstance(symbol, dict)
                and symbol.get("status") == "TRADING"
                and symbol.get("symbol", "").endswith("USDT")
            ):
                coins.append(symbol["symbol"])

        return coins[:limit]

    except Exception as e:
        st.error(f"Binance Error: {e}")
        return []


@st.cache_data(ttl=60)
def get_price(symbol):

    try:
        coin = symbol.replace("USDT", "")

        url = "https://min-api.cryptocompare.com/data/price"

        params = {
            "fsym": coin,
            "tsyms": "USD"
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        return data.get("USD")

    except:
        return None


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

    except:
        return []
