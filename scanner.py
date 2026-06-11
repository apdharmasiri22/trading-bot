import requests
import pandas as pd

# =========================
# TOP COINS (CoinGecko)
# =========================
def get_top_coins():

    try:
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

        coins = []

        for c in data:
            symbol = c.get("symbol", "").upper()

            # ❌ skip invalid base coins
            if symbol in ["USDT", "USD", "BUSD", "USDC"]:
                continue

            coins.append(symbol + "USDT")

        # safety fallback
        if not coins:
            coins = ["BTCUSDT"]

        return coins

    except Exception as e:
        print("TOP COINS ERROR:", e)
        return ["BTCUSDT"]


# =========================
# BINANCE MARKET DATA (KLINES)
# =========================
def get_market_data(symbol="BTCUSDT", interval="1h", limit=200):

    try:
        symbol = str(symbol).strip().upper()

        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        r = requests.get(url, params=params, timeout=10)

        # 🔥 DEBUG (IMPORTANT)
        print("STATUS:", r.status_code)
        print("RESPONSE:", r.text[:200])

        data = r.json()

        # Binance error handling
        if isinstance(data, dict):
            print("BINANCE ERROR:", data)
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            "time","Open","High","Low","Close","Volume",
            "c","q","n","t1","t2","t3"
        ])

        df = df[["Open","High","Low","Close","Volume"]].astype(float)

        return df

    except Exception as e:
        print("GET MARKET DATA ERROR:", e)
        return pd.DataFrame()
