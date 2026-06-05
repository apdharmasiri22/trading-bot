import requests
import streamlit as st


TOP_URL = "https://api.binance.com/api/v3/exchangeInfo"


@st.cache_data(ttl=3600)
def get_top_coins(limit=200):

    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        r = requests.get(url, timeout=10)
        data = r.json()

        coins = []

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    symbol = item.get("symbol")
                    if symbol and symbol.endswith("USDT"):
                        coins.append(symbol)

        # sort (important)
        coins = sorted(coins)

        # if API works, return full list
        if len(coins) > 20:
            return coins[:limit]

    except:
        pass

    # 🔥 BIG FALLBACK (expanded list)
    return [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
        "XRPUSDT", "ADAUSDT", "DOGEUSDT", "TRXUSDT",
        "AVAXUSDT", "MATICUSDT", "DOTUSDT", "LTCUSDT",
        "BCHUSDT", "LINKUSDT", "ATOMUSDT",
        "NEARUSDT", "ALGOUSDT", "FTMUSDT", "SANDUSDT",
        "APEUSDT", "APTUSDT", "OPUSDT", "ARBUsdt".upper()
    ][:limit]

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
