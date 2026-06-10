import requests
import pandas as pd

BINANCE_URL = "https://fapi.binance.com/fapi/v1/ticker/24hr"


def get_market_data():

    try:
        r = requests.get(BINANCE_URL, timeout=10)
        data = r.json()

        coins = []

        for c in data:

            if "symbol" not in c:
                continue

            coins.append({
                "Symbol": c["symbol"],
                "Price": float(c.get("lastPrice", 0)),
                "Change %": float(c.get("priceChangePercent", 0)),
                "Volume": float(c.get("volume", 0))
            })

        return pd.DataFrame(coins)

    except Exception as e:
        print("BINANCE ERROR:", e)
        return pd.DataFrame()
