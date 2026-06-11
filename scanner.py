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

    data = r.json()

    coins = []

    for c in data:

        symbol = c["symbol"].upper()

        # ✅ FIX: ONLY VALID FORMAT
        coins.append(symbol + "USDT")

    return coins


# =========================
# BINANCE OHLC DATA
# =========================
def get_market_data(symbol="BTCUSDT", interval="1h", limit=200):

    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"

        print("REQUEST URL:", url)

        data = requests.get(url, timeout=10).json()

        print("RAW RESPONSE:", data[:2])  # 🔥 DEBUG

        if isinstance(data, dict):
            print("ERROR RESPONSE:", data)
            return pd.DataFrame()

        df = pd.DataFrame(data)

        if df.empty:
            return df

        df = df.iloc[:, 0:6]
        df.columns = ["Time","Open","High","Low","Close","Volume"]

        df = df[["Open","High","Low","Close","Volume"]].astype(float)

        return df

    except Exception as e:
        print("ERROR:", e)
        return pd.DataFrame()
