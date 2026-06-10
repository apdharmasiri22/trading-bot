import requests
import pandas as pd

BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

def get_market_data():

    try:
        r = requests.get(BINANCE_URL, timeout=10)

        print("STATUS:", r.status_code)
        print("TEXT:", r.text[:200])

        if r.status_code != 200:
            return pd.DataFrame()

        data = r.json()

        coins = []

        for c in data:
            if "symbol" not in c:
                continue

            if not c["symbol"].endswith("USDT"):
                continue

            coins.append({
                "Symbol": c["symbol"],
                "Price": float(c.get("lastPrice", 0)),
                "Change %": float(c.get("priceChangePercent", 0)),
                "Volume": float(c.get("volume", 0))
            })

        return pd.DataFrame(coins)

    except Exception as e:
        print("ERROR:", e)
        return pd.DataFrame()
