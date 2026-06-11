import requests
import pandas as pd

# =========================
# COIN LIST
# =========================
def get_top_coins():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 20,
        "page": 1,
        "sparkline": False
    }

    r = requests.get(url, params=params, timeout=10)

    data = r.json()

    coins = []

    for c in data:
        symbol = c.get("symbol", "").upper()

        if symbol not in ["USDT", "USD"]:
            coins.append(symbol + "USDT")

    return coins


# =========================
# BINANCE OHLC
# =========================
def get_market_data(symbol="BTCUSDT", interval="1h", limit=200):

    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"

    data = requests.get(url, timeout=10).json()

    if isinstance(data, dict):
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=[
        "time","Open","High","Low","Close","Volume",
        "c","q","n","t1","t2","t3"
    ])

    df = df[["Open","High","Low","Close","Volume"]].astype(float)

    return df
