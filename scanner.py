import requests
import pandas as pd

# =========================
# COIN LIST (for dropdown)
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

    if r.status_code != 200:
        return ["BTCUSDT"]

    data = r.json()

    return [c["symbol"].upper() + "USDT" for c in data]


# =========================
# BINANCE OHLC DATA
# =========================
def get_market_data(symbol="BTCUSDT", interval="1h", limit=200):

    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url, timeout=10).json()

    if isinstance(data, dict):
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=[
        "time","Open","High","Low","Close","Volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    df = df[["Open","High","Low","Close","Volume"]].astype(float)

    return df
